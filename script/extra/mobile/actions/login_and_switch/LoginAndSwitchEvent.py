import time

from script.extra.mobile.base.BaseMobileEvent import BaseMobileEvent


# Result constants the Event returns to its Context.
SWITCHED = 'switched'
LOGGED_IN = 'logged_in'
SUSPENDED = 'suspended'
BATCH_FULL = 'batch_full'
FAILED = 'failed'

# The device, not the account, is the problem: a screen we couldn't recover
# from, or a UI element that never appeared. The account must NOT be marked
# bad for this — otherwise one stuck screen walks down the rotation flagging
# every account on the device as needing a login.
DEVICE_ERROR = 'device_error'


class LoginAndSwitchEvent(BaseMobileEvent):
    """
    Make device.account the active account on the device (the actual work;
    the Context wraps and fires this).

      * Already logged into this device -> switch via the account switcher
        (long-press profile_tab -> tap its row) -> SWITCHED.
      * Otherwise -> full login through Add account -> Log into existing ->
        username/password -> 2FA (pyotp) -> dismiss popups -> LOGGED_IN.
      * Challenge screen -> log out, return SUSPENDED.
      * 'Add account' gone -> BATCH_FULL (device already holds its 10 slots).

    Ported from the validated ig_multi_login.py prototype; the differences:
    creds come from device.account (not a txt file), switch-if-present is
    handled, and results map to instagram_state.

    Selectors live here, next to the only code that uses them (login is the
    one flow that needs them). Selector conventions handled by device.find():
    rid -> resource-id suffix, text -> exact, desc -> prefix. Text/desc values
    are English-locale. Activity names come from the device layer
    (device.HOME_ACTIVITIES / device.ACT_CHALLENGE).
    """

    # ── account switcher / add-account flow ─────────────────────────────────
    PROFILE_TAB = {'rid': 'profile_tab'}
    ADD_ACCOUNT = {'text': 'Add Instagram account'}
    LOG_INTO_EXISTING = {'text': 'Log into existing account'}
    USE_ANOTHER_PROFILE = {'desc': 'Use another profile'}

    # ── login form (content-desc based; IG appends dynamic bits -> prefix) ──
    LOGIN_USERNAME = {'desc': 'Username, email or mobile number,'}
    LOGIN_PASSWORD = {'desc': 'Password,'}
    LOGIN_SUBMIT = {'desc': 'Log in'}

    # ── 2FA ─────────────────────────────────────────────────────────────────
    TFA_CODE_FIELD = {'desc': 'Code,'}
    TFA_CONTINUE = {'desc': 'Continue'}

    # ── login error ─────────────────────────────────────────────────────────
    LOGIN_ERROR_TITLE = {'text': 'Unable to log in'}
    LOGIN_ERROR_OK = {'text': 'OK'}

    # ── suspended / challenge logout ────────────────────────────────────────
    CHALLENGE_MENU = {'desc': 'Menu'}
    CHALLENGE_LOGOUT_ITEM = {'text': 'Log out'}
    LOGOUT_CONFIRM = {'text': 'Log out'}

    # ── post-login popups / permissions ─────────────────────────────────────
    LOCATION_CONTINUE = {'text': 'Continue'}
    LOCATION_SERVICES_TITLE = {'text': 'How you can use Location Services'}
    PERM_DENY = {'rid': 'permission_deny_button'}
    LOCATION_SETTINGS_CANCEL = {'text': 'Cancel'}
    LOCATION_SETTINGS_GUARD = {'text': 'Open settings'}

    SUCCESS_POPUPS = [
        ({'text': 'Save'}, 'Save login info'),
        ({'text': 'Not now'}, 'Not now'),
        ({'text': 'Got it'}, 'Got it'),
    ]
    EXTRA_DISMISS_BUTTONS = ['OK', 'Skip', 'Dismiss', 'Close']

    @staticmethod
    def _account_row(username):
        # The logged-in account's row in the switcher is keyed by its username.
        return {'text': username}

    # ── entry ───────────────────────────────────────────────────────────────
    def init(self):
        self.log(f'activating {self.account.username}')

        # go_home() already falls back to a hard restart, so failing here means
        # the app itself is unusable — a device problem, not an account one.
        if not self._ensure_home():
            self.log('could not reach Home even after restarting Instagram')
            return DEVICE_ERROR

        if self._switch_if_logged_in():
            return SWITCHED

        return self._fresh_login()

    # ── home / navigation ───────────────────────────────────────────────────
    def _ensure_home(self):
        # Verified by the tab bar, not the activity name: a reels viewer left
        # open by a previous module keeps the same activity, which used to make
        # this return True and then fail to find profile_tab.
        return self.device.go_home()

    # ── switch path ─────────────────────────────────────────────────────────
    def _switch_if_logged_in(self):
        if not self._open_account_switcher():
            return False

        # The switcher list scrolls: with up to 10 accounts on a device, the
        # target is often below the fold. Checking a single dump would wrongly
        # conclude "not logged in" and trigger a full login for an account
        # that's already there, so scroll before giving up.
        self.log(f'looking for {self.account.username} in the account switcher')
        row = self.device.find_or_scroll(
            self._account_row(self.account.username), max_scrolls=4
        )
        if not row:
            self.log('account not in switcher; will do a full login')
            return False

        self.log(f'switching to {self.account.username}')
        self.device.tap(row[0], row[1])
        time.sleep(3)
        return self._ensure_home()

    def _open_account_switcher(self):
        self.log('opening account switcher (long-press profile tab)')
        hit = self.device.wait_for(self.PROFILE_TAB, timeout=15)
        if not hit:
            # Home was verified moments ago, so this means the screen moved
            # under us. Reset once and try again rather than giving up.
            self.log('profile tab missing; restarting Instagram and retrying')
            if not self.device.hard_reset():
                return False
            hit = self.device.wait_for(self.PROFILE_TAB, timeout=15)
        if not hit:
            self.log('profile tab still not found')
            return False
        # 800ms did not register on the real device; 1200ms opens the sheet
        # reliably, and it needs ~3s to animate in before a dump is meaningful.
        self.device.long_press(hit[0], hit[1], ms=1200)
        time.sleep(3)
        return True

    # ── fresh login path ────────────────────────────────────────────────────
    def _fresh_login(self):
        d = self.device
        self.log(f'full login for {self.account.username}')

        if not self._open_account_switcher():
            return DEVICE_ERROR

        if d.find_or_scroll(self.ADD_ACCOUNT, max_scrolls=5) is None:
            self.log('device already holds its account slots (Add account gone)')
            return BATCH_FULL

        self.log("tapping 'Add Instagram account'")
        if not d.tap_selector(self.ADD_ACCOUNT):
            return FAILED
        time.sleep(2)

        self.log("tapping 'Log into existing account'")
        if not d.tap_selector(self.LOG_INTO_EXISTING):
            return FAILED
        time.sleep(2)

        if d.find_or_scroll(self.USE_ANOTHER_PROFILE, max_scrolls=6):
            self.log("tapping 'Use another profile'")
            d.tap_selector(self.USE_ANOTHER_PROFILE)
            time.sleep(2)

        if not self._fill_credentials():
            return FAILED

        if self._has_login_error():
            return FAILED

        if not self._handle_2fa():
            return FAILED

        if d.foreground_activity_name() == d.ACT_CHALLENGE:
            self._logout_suspended()
            return SUSPENDED

        self.log('login submitted OK; dismissing post-login popups')
        self._dismiss_popups()
        self.log(f'{self.account.username} logged in')
        return LOGGED_IN

    def _fill_credentials(self):
        d = self.device

        self.log('entering username')
        if not d.tap_selector(self.LOGIN_USERNAME):
            return False
        d.clear_field()
        d.type_text(self.account.username)
        time.sleep(0.5)

        self.log('entering password')
        if not d.tap_selector(self.LOGIN_PASSWORD):
            return False
        d.clear_field()
        d.type_text(self.account.password)
        time.sleep(0.5)

        self.log('submitting login form')
        if not d.tap_selector(self.LOGIN_SUBMIT):
            return False
        time.sleep(5)
        return True

    def _handle_2fa(self):
        d = self.device

        tfa = d.wait_for(self.TFA_CODE_FIELD, timeout=12)
        if not tfa:
            return True  # no 2FA prompt

        self.log('2FA prompt; entering code')
        code = self.account.get_verification_code()
        if not code:
            self.log('2FA prompt but no secret_key on the account')
            return False

        d.tap(tfa[0], tfa[1])
        d.clear_field()
        d.type_text(code)
        time.sleep(0.5)
        d.tap_selector(self.TFA_CONTINUE)
        time.sleep(6)
        return not self._has_login_error()

    def _has_login_error(self):
        d = self.device
        xml = d.dump_xml()
        if d.find(xml, self.LOGIN_ERROR_TITLE) or d.find(xml, self.LOGIN_ERROR_OK):
            self.log("'Unable to log in' error")
            ok = d.find(xml, self.LOGIN_ERROR_OK)
            if ok:
                d.tap(ok[0], ok[1])
                time.sleep(2)
            self._ensure_home()
            return True
        return False

    # ── suspended ───────────────────────────────────────────────────────────
    def _logout_suspended(self):
        d = self.device
        self.log('account suspended (challenge); logging out')

        d.tap_selector(self.CHALLENGE_MENU, timeout=10)
        time.sleep(1.5)
        if not d.tap_selector(self.CHALLENGE_LOGOUT_ITEM, timeout=10):
            d.press_back()
            return
        time.sleep(1.5)
        d.tap_selector(self.LOGOUT_CONFIRM, timeout=10)
        time.sleep(3)

    # ── post-login popups ───────────────────────────────────────────────────
    def _dismiss_popups(self):
        d = self.device

        for _ in range(6):
            xml = d.dump_xml()

            loc = d.find(xml, self.LOCATION_CONTINUE)
            if loc and d.find(xml, self.LOCATION_SERVICES_TITLE):
                d.tap(loc[0], loc[1])
                time.sleep(2)
                continue

            perm = d.find(xml, self.PERM_DENY)
            if perm:
                d.tap(perm[0], perm[1])
                time.sleep(2)
                continue

            cancel = d.find(xml, self.LOCATION_SETTINGS_CANCEL)
            if cancel and d.find(xml, self.LOCATION_SETTINGS_GUARD):
                d.tap(cancel[0], cancel[1])
                time.sleep(2)
                continue

            acted = False
            for sel, _label in self.SUCCESS_POPUPS:
                hit = d.find(xml, sel)
                if hit:
                    d.tap(hit[0], hit[1])
                    time.sleep(2)
                    acted = True
                    break
            if acted:
                continue

            for label in self.EXTRA_DISMISS_BUTTONS:
                hit = d.find(xml, {'text': label})
                if hit:
                    d.tap(hit[0], hit[1])
                    time.sleep(2)
                    acted = True
                    break
            if not acted:
                return