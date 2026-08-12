class IGSelectors:
    """
    Instagram UI selectors and activity names, lifted verbatim from the
    validated login prototype (ig_multi_login.py). Kept in one place so a UI
    change only needs editing here. These are stable resource-ids / text /
    content-desc values observed on the real app; text/desc are English-locale.
    """

    # ── activities (from foreground_activity) ───────────────────────────────
    ACT_HOME = 'MainTabActivity'
    ACT_HOME_ALT = 'InstagramMainActivity'
    ACT_MODAL = 'ModalActivity'
    ACT_CHALLENGE = 'ChallengeActivity'   # suspended / challenge screen

    HOME_ACTIVITIES = (ACT_HOME, ACT_HOME_ALT)

    # ── account switcher / add flow ─────────────────────────────────────────
    PROFILE_TAB = {'rid': 'profile_tab'}
    ADD_ACCOUNT = {'text': 'Add Instagram account'}
    LOG_INTO_EXISTING = {'text': 'Log into existing account'}
    USE_ANOTHER_PROFILE = {'desc': 'Use another profile'}

    # ── login form (content-desc based; IG appends dynamic bits, use prefix) ─
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

    # ── success / permission popups ─────────────────────────────────────────
    POPUP_SAVE_INFO = {'text': 'Save'}
    POPUP_NOT_NOW = {'text': 'Not now'}
    POPUP_GOT_IT = {'text': 'Got it'}

    SUCCESS_POPUPS = [
        (POPUP_SAVE_INFO, 'Save login info'),
        (POPUP_NOT_NOW, 'Not now'),
        (POPUP_GOT_IT, 'Got it'),
    ]

    LOCATION_CONTINUE = {'text': 'Continue'}
    LOCATION_SERVICES_TITLE = {'text': 'How you can use Location Services'}
    PERM_DENY = {'rid': 'permission_deny_button'}
    LOCATION_SETTINGS_CANCEL = {'text': 'Cancel'}
    LOCATION_SETTINGS_GUARD = {'text': 'Open settings'}

    EXTRA_DISMISS_BUTTONS = ['OK', 'Skip', 'Dismiss', 'Close']

    # ── the logged-in account row in the switcher (text = username) ─────────
    @staticmethod
    def account_row(username):
        return {'text': username}
