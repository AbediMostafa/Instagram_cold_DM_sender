from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Proxy import Proxy
from script.extra.helper import tehran_now


class Mobile(BaseWithTimeZoneModel):
    """
    One DuoPlus cloud phone — the unit of work on the mobile side (mirror of
    what an Account is on the web side, and of the Process row for a worker).

    `status` is the *physical* device state as last reported by DuoPlus
    (written by the central status sync and by boot polling). `app_state` is
    the *logical* worker state, exactly like the account app_state on web.
    The two are independent: a phone can be powered on (status=1) while no
    worker is using it (app_state=idle).
    """

    duo_id = CharField(unique=True)
    name = CharField()

    # DuoPlus cloudPhone/status codes. Only STATUS_ON is usable.
    status = IntegerField(default=0)
    app_state = CharField(default='idle')

    proxy = ForeignKeyField(Proxy, backref='mobiles', null=True)

    # Heartbeat for the stuck-reset (phase 9): the worker touches this on
    # every cycle, so a processing state older than the timeout means the
    # worker died and app_state can be released.
    updated_at = DateTimeField(null=True)

    STATUS_NOT_CONFIGURED = 0
    STATUS_ON = 1
    STATUS_OFF = 2
    STATUS_EXPIRED = 3
    STATUS_RENEWAL_NEEDED = 4
    STATUS_POWERING_ON = 10
    STATUS_CONFIGURING = 11
    STATUS_CONFIG_FAILED = 12

    # Dead-end statuses: no amount of polling will make these usable.
    UNUSABLE_STATUSES = [STATUS_NOT_CONFIGURED, STATUS_EXPIRED,
                         STATUS_RENEWAL_NEEDED, STATUS_CONFIG_FAILED]

    # Transitional statuses worth polling on.
    TRANSITIONAL_STATUSES = [STATUS_POWERING_ON, STATUS_CONFIGURING]

    class Meta:
        table_name = 'mobiles'

    # ── state helpers ───────────────────────────────────────────────────────
    def set_app_state(self, state):
        """Set the logical worker state and refresh the heartbeat together."""
        self.app_state = state
        self.updated_at = tehran_now()
        self.save()

    def heartbeat(self):
        """Touch updated_at so the stuck-reset knows this worker is alive."""
        self.updated_at = tehran_now()
        self.save()

    def set_status(self, status_code):
        """Record the physical device status reported by DuoPlus."""
        self.status = int(status_code)
        self.save()

    def is_usable(self):
        return self.status == self.STATUS_ON

    # ── relations ───────────────────────────────────────────────────────────
    def accounts(self):
        """
        The accounts this device rotates through: assigned to it, enabled, in a
        usable Instagram state, AND not yet used this round (is_used == 0).

        Mirrors the browser's get_next_account, which claims is_used=0 accounts
        and resets them all back to 0 once the pool is exhausted. Here the
        device cycles its unused accounts; MobileProcessManager marks each
        is_used=True after its session and resets the whole set to 0 when none
        remain, so rotation spreads evenly instead of always starting at the
        lowest id.

        No atomic claim is needed - assignment is exclusive by design. The
        instagram_state filter mirrors get_next_account on the web side: an
        account that is suspended or needs a login has already failed, and
        retrying it every rotation would burn minutes of rate-limited API calls
        for nothing. Clearing the state in the panel puts it back in service.
        """
        from .Account import Account

        return (
            Account
            .select()
            .where(
                (Account.mobile == self) &
                (Account.is_active == 1) &
                (Account.is_used == 0) &
                (Account.instagram_state == 'active')
            )
            .order_by(Account.id)
        )

    def all_assigned_accounts(self):
        """
        Every usable account on this device regardless of is_used - used to
        decide whether an empty accounts() means 'all used this round' (so
        reset) versus 'device genuinely has no accounts'.
        """
        from .Account import Account

        return (
            Account
            .select()
            .where(
                (Account.mobile == self) &
                (Account.is_active == 1) &
                (Account.instagram_state == 'active')
            )
            .order_by(Account.id)
        )

    def reset_used_accounts(self):
        """
        Start a fresh rotation: clear is_used on all this device's accounts.
        Only touches active accounts, like the browser's resetIsUsed, so a
        suspended account isn't silently brought back into rotation.
        """
        from .Account import Account

        return (
            Account
            .update(is_used=False)
            .where(
                (Account.mobile == self) &
                (Account.is_active == 1) &
                (Account.instagram_state == 'active')
            )
            .execute()
        )

    def add_cli(self, log):
        # Same convention as Process.add_cli / Account.add_cli: prefix and
        # print. DB writes stay disabled to keep write load down.
        print(f'[mobile {self.id} -- {self.duo_id}] ${log}')
        return False