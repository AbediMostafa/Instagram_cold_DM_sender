import os
import sys
import time
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from script.models.Mobile import Mobile
from script.models.Process import Process
from script.extra.exceptions import ProcessShouldStop

load_dotenv()


class MobileProcessManager:
    """
    One work cycle for one DuoPlus device — the mobile mirror of
    ProcessManager, and deliberately as close to it as possible.

    A mobile worker registers in the SAME processes table as a web worker, so
    it inherits the whole control surface: the panel lists it, assigns its
    workflow, and starts or stops it via processes.status. The only mobile
    specific part is processes.mobile_id, which pins the row to a device —
    web processes are interchangeable, mobile ones are not.

    Everything the operator controls therefore lives on the process row
    (status, workflow); the mobiles table stays pure device inventory
    (duo_id, physical status, app_state, proxy).

    The unit of work is the device: it owns a fixed set of accounts and cycles
    through all of them, giving each a session. No account claim is needed
    (fixed assignment); only order claims compete across devices, and a stuck
    app_state=processing is released by staleness on updated_at.
    """

    sleep_time = 20

    def __init__(self, mobile_id=None):
        # The device is normally pinned at launch (--mobile-id). If it isn't,
        # the process row's mobile_id is used, so a device can be assigned
        # entirely from the panel.
        self.mobile_id = mobile_id
        self.process = None
        self.mobile = None
        self.workflow = None
        self.service = None
        self.modules = None
        self.device = None  # BaseDuoPlus instance

    # ── cycle ───────────────────────────────────────────────────────────────
    def run(self):
        try:
            # init() is inside the try, unlike the web ProcessManager. There a
            # transient database error kills one of thirty interchangeable
            # workers; here it would take a whole device offline until someone
            # relaunches it, so the worker sleeps and retries instead.
            self.init()

            self.check_stop_statuses()
            self.reset_stuck_mobiles()
            self.get_modules()
            self.boot()
            self.start()

        except ProcessShouldStop as e:
            self._log(str(e))
            time.sleep(self.sleep_time)

        except Exception as e:
            self._log(str(e))
            self._log(traceback.format_exc())
            time.sleep(self.sleep_time)

    def init(self):
        """
        Register in the processes table and load this cycle's config from it.
        Reloaded every cycle so panel changes (workflow, start/stop) take
        effect without restarting the worker — exactly like the web side.
        """
        self.mobile = self._resolve_mobile()

        if self.mobile is None:
            # Register anyway so the row exists in the panel and an operator can
            # see the worker and assign it a device.
            self.process = Process.update_or_create_process(os.getpid())
            self.workflow = self.service = self.modules = None
            return

        self.process = Process.register_mobile_worker(os.getpid(), self.mobile)

        self.workflow = self.process.workflow
        if self.workflow:
            self.service = self.workflow.service
            self.modules = self._mobile_modules()

    def _resolve_mobile(self):
        """Device from the launch argument, falling back to the process row."""
        if self.mobile_id is not None:
            return Mobile.get_or_none(Mobile.id == self.mobile_id)

        process = Process.get_or_none(
            (Process.pid == os.getpid()) &
            (Process.server_ip == Process.get_server_ip())
        )
        return process.mobile if process and process.mobile_id else None

    def _mobile_modules(self):
        """
        Only type=mobile modules of this workflow, ordered by priority.
        Builds on Workflow.modules() (same join the web side uses) instead of
        re-implementing the relation.
        """
        from script.models.Module import Module

        return list(
            self.workflow.modules()
            .where(Module.type == 'mobile')
            .order_by(Module.priority.asc())
        )

    def check_stop_statuses(self):
        """Guards: any failure raises ProcessShouldStop -> sleep and retry."""
        if self.process is None:
            raise ProcessShouldStop(
                f'Not registered in the processes table; '
                f'sleeping {self.sleep_time}s ...'
            )

        if self.mobile is None:
            raise ProcessShouldStop(
                f'No device assigned to this process; '
                f'sleeping {self.sleep_time}s ...'
            )

        # The panel's start/stop switch, identical to the web side: a process
        # is only allowed to work while its status is 'running'.
        if self.process.status in Process.stopped_process:
            raise ProcessShouldStop(
                f"Process status is '{self.process.status}'; "
                f'sleeping {self.sleep_time}s ...'
            )

        if self.mobile.app_state == 'error':
            raise ProcessShouldStop(
                f'Mobile in error state; sleeping {self.sleep_time}s ...'
            )

        if self.workflow is None:
            raise ProcessShouldStop(
                f'No workflow assigned to this process; '
                f'sleeping {self.sleep_time}s ...'
            )

        if self.service is None:
            raise ProcessShouldStop(
                f'No service assigned to this workflow; '
                f'sleeping {self.sleep_time}s ...'
            )

        if not self.modules:
            raise ProcessShouldStop(
                f'No mobile modules assigned to this workflow; '
                f'sleeping {self.sleep_time}s ...'
            )

        if self.service.should_run() is False:
            raise ProcessShouldStop(
                f"Service says don't run; sleeping {self.sleep_time}s ..."
            )

    def get_modules(self):
        titles = [m.title for m in self.modules]
        self._log(f'workflow: {self.workflow.title}, '
                  f'service: {self.service.service}, modules: {titles}')

    def boot(self):
        """
        Bring the device up (startup recovery only — always-on policy). A
        dead-end device is parked in app_state=error so the guard skips it
        next cycle instead of hammering powerOn.
        """
        from script.extra.mobile.base.BaseDuoPlus import BaseDuoPlus, MobileUnusable

        self.device = BaseDuoPlus(self.mobile)

        # Expose the panel stop switch to events (ShareEvent checks it between
        # sends so stop takes effect inside a share window, not only between
        # account switches).
        self.device.stop_check = self._stop_requested

        try:
            self.device.init()
        except MobileUnusable as e:
            self.mobile.set_app_state('error')
            raise ProcessShouldStop(f'Mobile unusable: {e}')

    # ── work ────────────────────────────────────────────────────────────────
    def start(self):
        """
        Mark the device busy, then run one session per assigned account.

        The stop switch is re-read before every account, not just once per
        cycle. On the web a cycle is a single account, so returning to the
        t.py loop re-checks the guards constantly; here a cycle is the whole
        device rotation, which can run for the best part of an hour. Without
        this check, pressing stop in the panel would appear to do nothing.

        Account switching is the natural stopping point — it's the mobile
        equivalent of the browser and profile closing between web accounts.

        The finally block always releases the device back to idle and never
        powers the phone off.
        """
        from script.extra.mobile.SessionRunner import SessionRunner

        self.mobile.set_app_state('processing')

        try:
            accounts = list(self.mobile.accounts())

            # Browser-style rotation: accounts() only returns is_used=0 accounts
            # for THIS device. An empty list can mean the device has no usable
            # accounts at all, OR that every account was already used — in the
            # latter case, reset this device's set to 0 and start a fresh round
            # (mirrors the web resetIsUsed when get_next_account runs dry).
            if not accounts:
                if self.mobile.all_assigned_accounts().count() > 0:
                    reset = self.mobile.reset_used_accounts()
                    self._log(f'all accounts used; reset {reset} and starting '
                              f'a new round')
                    accounts = list(self.mobile.accounts())
                else:
                    self._log('Mobile has no usable accounts assigned')
                    return

            total = len(accounts)
            completed = 0
            for index, account in enumerate(accounts, start=1):
                if self._stop_requested():
                    self._log(
                        f'Stopped from the panel; halting after '
                        f'{index - 1}/{total} account(s)'
                    )
                    return

                runner = SessionRunner(
                    device=self.device,
                    account=account,
                    modules=self.modules,
                    service=self.service,
                    mobile=self.mobile,
                )
                runner.run()

                # Mark this account used for the round so the next rotation
                # picks a different one and the load spreads evenly. Atomic
                # single-row UPDATE; no lock needed (the device owns it).
                from script.models.Account import Account
                Account.update(is_used=True).where(
                    Account.id == account.id
                ).execute()
                completed += 1

                # Heartbeat between accounts so a rotation that runs for many
                # minutes isn't mistaken for a stuck worker.
                self.mobile.heartbeat()

            # Round complete: every unused account was processed. Reset this
            # device's set so the NEXT run() starts a fresh round immediately —
            # rotation is continuous (the launcher calls run() again right
            # away), but each round still returns here first so panel changes
            # (workflow/stop) and stuck-resets are re-read once per round.
            if completed == total:
                reset = self.mobile.reset_used_accounts()
                self._log(f'round complete ({completed}/{total} account(s)); '
                          f'reset {reset} for the next round')

        finally:
            if self.device:
                self.device.cleanup()
            # Release the logical state; the phone stays powered on.
            self.mobile.set_app_state('idle')

    def _stop_requested(self):
        """
        Re-read this worker's process row and report whether it should stop.

        Deliberately re-queried rather than trusting the copy loaded at the
        start of the cycle: the whole point is to notice a change an operator
        made while the rotation was already running. A failed read is treated
        as "keep going", so a transient database hiccup can't silently park a
        healthy worker.
        """
        if self.process is None:
            return False

        try:
            process = Process.get_or_none(Process.id == self.process.id)
        except Exception as e:
            self._log(f'could not re-read process status: {e}')
            return False

        if process is None:
            return False

        self.process = process
        return process.status in Process.stopped_process

    # ── stuck-reset (phase 9) ───────────────────────────────────────────────
    def reset_stuck_mobiles(self):
        """
        Release mobiles stuck in app_state=processing whose heartbeat has gone
        stale — the worker died mid-session.

        No lock is taken, unlike the web-side _reset_stuck_orders. This sweep
        is a single state-conditioned UPDATE, which is exactly the pattern the
        whole system is built on: it's atomic and idempotent, so several
        workers running it in the same second is harmless — the first one wins
        and the rest match zero rows.
        """
        from script.models.Setting import Setting
        from script.extra.helper import tehran_now
        from datetime import timedelta

        timeout = int(Setting.get_value('mobile_stuck_timeout_seconds', 900))
        cutoff = tehran_now() - timedelta(seconds=timeout)

        updated = (
            Mobile
            .update(app_state='idle')
            .where(
                (Mobile.app_state == 'processing') &
                (Mobile.updated_at.is_null(False)) &
                (Mobile.updated_at < cutoff)
            )
            .execute()
        )

        if updated > 0:
            self._log(f'Reset {updated} stuck mobile(s)')

    # ── logging ─────────────────────────────────────────────────────────────
    def _log(self, msg):
        if self.mobile:
            self.mobile.add_cli(msg)
        elif self.process:
            self.process.add_cli(msg)
        else:
            print(f'[mobile worker] {msg}')