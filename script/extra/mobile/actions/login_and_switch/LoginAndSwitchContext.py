from script.extra.exceptions import CantPerformAction
from script.extra.mobile.base.MobileMiddleware import MobileMiddleware
from .LoginAndSwitchEvent import (
    LoginAndSwitchEvent,
    SWITCHED, LOGGED_IN, SUSPENDED, BATCH_FULL, FAILED, DEVICE_ERROR,
)


class LoginAndSwitchContext(MobileMiddleware):
    """
    Entry point for making the session account active (mirror of LoginContext).

    Runs first in a session. No eligibility strategies for now — a login/switch
    is always attempted — but the hook is here (`strategies = [...]`) if e.g. a
    "don't re-login within N minutes" guard is wanted later.

    Contract for SessionRunner: execute() returns True if the account is now
    active and usable, False if the session should skip this account. The Event
    result is translated to instagram_state here so the panel reflects reality.
    """

    strategies = []

    def execute(self):
        try:
            self.cant_perform()
        except CantPerformAction as e:
            self.log(f'skipping login/switch: {e}')
            return False

        result = LoginAndSwitchEvent(self.device).init()

        if result == SWITCHED:
            self.account.set_state('active')
            self.log('switched to already-logged-in account')
            return True

        if result == LOGGED_IN:
            self.account.set_state('active')
            self.log('logged in fresh')
            return True

        if result == SUSPENDED:
            self.account.set_state('suspended')
            self.account.add_warning('suspended on mobile (challenge)')
            return False

        if result == DEVICE_ERROR:
            # Deliberately leaves instagram_state alone. The account never got
            # far enough to prove anything about itself, and marking it here
            # would let a single stuck screen flag every account on the device.
            self.log('device problem, not an account problem; skipping this round')
            return False

        if result == BATCH_FULL:
            # Device already holds its 10 accounts but not this one — a config
            # problem (too many accounts assigned). Skip, don't retry.
            self.log('device account slots full; cannot add this account')
            return False

        # FAILED. 'login required' is the project's existing state for this;
        # accounts.instagram_state is a DB enum, so an invented value like
        # 'login_failed' is rejected outright by the check constraint.
        self.account.set_state('login required')
        return False