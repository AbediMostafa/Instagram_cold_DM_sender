import time
import traceback

from script.extra.helper import tehran_now
from script.extra.exceptions import RetryableError
from script.extra.mobile.base.BaseMobileEvent import BaseMobileEvent
from script.extra.mobile.base.BaseDuoPlus import DeviceCommandError
from script.extra.mobile.base.LinkParser import LinkParser
from script.models.Setting import Setting
from script.models.Order import Order
from script.models.OrderAction import (
    OrderAction,
    get_single_action_for_account_prepared,
    mark_share_action_completed,
    reset_stuck_processing_actions,
)

from .ShareMechanics import ShareMechanics, ShareGroupsUnavailable


class ShareEvent(BaseMobileEvent):
    """
    Share execution: within a time window (mobile_share_seconds, default 300)
    claim FREE share actions from prepared orders and fire one send each.

    Because SharePrepare created every action upfront with its count, this
    loop never computes remaining amounts: claim -> send count//per_group
    groups -> mark sent -> completed_count += count. Two devices can never
    overshoot a total; when no free action is left, the order is done.

    Hard rules honored here:
      - The time check runs BEFORE each send; a send that started always runs
        to completion (no half-ticked sheets abandoned).
      - The panel stop switch (device.stop_check, wired by
        MobileProcessManager) is also checked between sends, so a stop takes
        effect inside the 5-minute window, not only between accounts.
      - An account never claims an order it prepared or shared before —
        get_single_action_for_account_prepared enforces that via the
        account's existing OrderAction rows.
      - Window over => return, handing control back to SessionRunner so the
        rest of the workflow still runs.
    """

    # Two device-level failures in a row usually means the phone/app is in a
    # bad state; stop burning the window and let the rest of the session run.
    MAX_CONSECUTIVE_FAILURES = 2

    def init(self):
        window_seconds = int(Setting.get_value('mobile_share_seconds', 300))
        per_group = int(Setting.get_value('mobile_share_per_group', 250))
        stuck_timeout = int(Setting.get_value('mobile_share_stuck_timeout', 120))

        self._reset_stuck_actions(stuck_timeout)

        mechanics = ShareMechanics(self.device)
        started_at = time.time()
        session_excluded = []
        sends_done = 0
        consecutive_failures = 0
        next_heartbeat = started_at + 60  # "still working" ping every minute

        while True:
            now = time.time()
            elapsed = int(now - started_at)

            # Heartbeat: independent of the per-send logs, so even during a
            # long send (or a quiet stretch) the console shows the module is
            # alive and how much of the window is left.
            if now >= next_heartbeat:
                remaining = max(0, window_seconds - elapsed)
                self.log(f'still sharing... {elapsed}s elapsed, '
                         f'{remaining}s left, {sends_done} send(s) so far')
                next_heartbeat = now + 60

            if elapsed >= window_seconds:
                self.log(f'share window over ({sends_done} send(s) this session)')
                return

            if self._stop_requested():
                self.log('panel stop requested; leaving share loop')
                return

            self.log(f'looking for next share action (t={elapsed}s/{window_seconds}s)')
            action = get_single_action_for_account_prepared(
                self.account, ['share'], excluded_order_ids=session_excluded
            )

            if not action:
                if sends_done == 0:
                    self.log('no share actions available for this account')
                else:
                    self.log(f'share queue drained ({sends_done} send(s))')
                return

            order = Order.get_by_id(action.order_id)
            groups = self._action_groups(action, per_group)

            self.log(
                f'send #{sends_done + 1} for order #{order.id}: action #{action.id} '
                f'count={action.count} ({groups} groups)'
            )

            try:
                parsed = self._target_from_order(order)
                self.log(f'opening {parsed.get("type")} target')
                mechanics.open_target(parsed)
                self.log('target opened, pressing share and selecting groups')
                sent = mechanics.perform_send(parsed['type'], groups)
                self.log(f'SUCCESS - sent to {sent} group(s)')

                if mark_share_action_completed(action):
                    sends_done += 1
                    consecutive_failures = 0
                    self.log(
                        f'counted: order #{order.id} '
                        f'completed_count += {action.count}'
                    )
                else:
                    # A stuck-reset raced us and freed the action after we
                    # sent. The share went out but can't be counted twice;
                    # log loudly and move on.
                    self.log(
                        f'action #{action.id} was no longer ours after the '
                        f'send; not counted'
                    )

            except ShareGroupsUnavailable as e:
                # This account's groups can't cover the send; other orders
                # would hit the same wall, so leave the loop entirely.
                self.log(str(e))
                action.reset_to_free()
                return

            except (RetryableError, TimeoutError, DeviceCommandError) as e:
                self.log(f'retryable failure on order #{order.id}: {e}')
                action.reset_to_free()
                session_excluded.append(order.id)
                consecutive_failures += 1
                if consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                    self.log('too many consecutive failures; leaving share loop')
                    return
                try:
                    self.device.go_home()
                except Exception:
                    pass

            except Exception as e:
                # Permanent target failure discovered mid-order (deleted or
                # made private after prepare): cancel like the preparer would.
                # Share is balance-exempt, so cancel carries no charge.
                self.log(f'order #{order.id} failed permanently: {e}')
                self.account.add_log(traceback.format_exc())
                action.reset_to_free()

                Order.update(
                    status='Canceled',
                    description=str(e),
                    updated_at=tehran_now()
                ).where(
                    (Order.id == order.id) &
                    (Order.status != 'Completed')
                ).execute()

                session_excluded.append(order.id)

    # ── helpers ─────────────────────────────────────────────────────────────
    @staticmethod
    def _action_groups(action, per_group):
        """
        Real group count for an action: stored in `content` by the preparer.
        Falls back to a ceil of the count for any legacy row without it.
        """
        if action.content:
            try:
                return max(1, int(action.content))
            except (TypeError, ValueError):
                pass
        return max(1, (action.count + per_group - 1) // per_group)

    def _target_from_order(self, order):
        """
        Navigation info comes from action_data written by prepare; the raw
        link is only the fallback for orders prepared before this field or
        with partial data.
        """
        data = order.action_data or {}

        if data.get('type'):
            return {
                'type': data.get('type'),
                'post_code': data.get('post_code'),
                'username': data.get('username'),
                'story_id': data.get('story_id'),
            }

        parsed = LinkParser.parse(order.target_link)
        if parsed.get('type') not in (LinkParser.TYPE_POST,
                                      LinkParser.TYPE_REEL,
                                      LinkParser.TYPE_STORY):
            raise Exception(f"order link unusable ({parsed.get('type')})")
        return parsed

    def _reset_stuck_actions(self, stuck_timeout):
        """
        Free share actions a dead worker left in 'processing' — the
        action-level twin of the order-level is_prepared reset. Lock keeps
        the frequency down; the UPDATE itself is race-safe without it.
        """
        try:
            from script.models.Lock import Lock
            if not Lock.acquire('mobile_share_action_reset', duration_seconds=60):
                return
            acquired = True
        except ImportError:
            acquired = False

        try:
            freed = reset_stuck_processing_actions(['share'], stuck_timeout)
            if freed:
                self.log(f'freed {freed} stuck share action(s)')
        finally:
            if acquired:
                from script.models.Lock import Lock
                Lock.release('mobile_share_action_reset')

    def _stop_requested(self):
        """
        The panel stop switch, exposed on the device by MobileProcessManager.
        Absent hook (tests, older manager) just means no mid-window stop.
        """
        stop_check = getattr(self.device, 'stop_check', None)
        if not callable(stop_check):
            return False
        try:
            return bool(stop_check())
        except Exception as e:
            self.log(f'stop check failed: {e}')
            return False