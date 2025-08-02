import traceback
from instagrapi.exceptions import PleaseWaitFewMinutes, LoginRequired


class InstagramErrorHandler:
    account = None

    def __init__(self, account):
        self.account = account

    def handle_client_forbidden_exception(self, e):
        if 'There is a limit to the number of new conversations you can start' in e:
            self.account.set_state('doesnt followed dm limit', 'instagram_state', e)

        self.account.add_warning(e,10)
        raise Exception(e)

    def handle_feedback_required_exception(self, e):
        if 'We limit how often you can do certain things on Instagram' in e:
            self.account.set_state('follow ban')

            self.account.add_warning(e,10)
            raise Exception(e)

        if 'Some accounts prefer to manually review followers' in e:
            self.account.add_cli(e,8)
            self.account.add_log(traceback.format_exc())


    def handle_client_not_found_exception(self, e):
        self.account.add_warning(e,10)
        raise Exception(e)

    def handle_client_connection_error(self, e):

        self.account.add_warning(e,8)
        raise Exception(e)

    def handle_proxy_blocked_exception(self, e):
        self.account.set_state('proxy blocked', 'instagram_state', e)
        self.account.add_warning(e, 8)

        raise Exception(e)

    def handle_account_challenging_exception(self, e):
        self.account.set_state('challenging', 'instagram_state', e)
        self.account.add_warning(e, 24)

        raise Exception(e)

    def handle_wait_a_few_minutes_exception(self, e):
        self.account.set_state('wait a few minutes', 'instagram_state', e)
        self.account.add_warning(e,6)
        raise PleaseWaitFewMinutes(e)

    def handle_two_factor_required_exception(self, e):
        self.account.set_state('two factor required', 'instagram_state', e)
        self.account.add_warning(e,24)

        raise Exception(e)

    def handle_login_required_exception(self, e):
        # self.account.set_state('login required', 'instagram_state', e)
        # self.account.add_warning(e)

        raise LoginRequired(e)

    def handle_general_exceptions(self, e):
        self.handle_exception(e)

    def handle_exception(self, reason, _type='raise'):
        self.account.add_cli(reason)
        self.account.add_log(traceback.format_exc())

        if _type == 'raise':
            raise Exception(reason)
