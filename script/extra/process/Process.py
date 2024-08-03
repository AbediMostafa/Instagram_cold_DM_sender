from script.extra.instagram.InstagramMobile import InstagramMobile
from script.models.AccountHelper import *
from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy


class Process:
    account = None
    name_command = None
    username_command = None
    avatar_command = None
    ig = None
    igMobile = None
    follow = None

    def start(self):
        try:
            self.account = get_next_account()
            self.igMobile = InstagramMobile(self.account)
            self.account.set_state('processing', 'app_state')
            self.igMobile.set_proxy().log_in()
            self.do_process()
            self.after_process_hooks()

        except Exception as e:
            if 'user with that username already exists' in str(e) or "username isn't available" in str(
                    e) or 'Enter a name under 30 characters' in str(
                e) or "You can't end your username with a period" in str(e):
                pass

        finally:
            self.account.set_state('idle', 'app_state')

    def do_process(self):
        HowManyEventsCanHandleStrategy(self.account, self.igMobile).run()

    def after_process_hooks(self):
        CheckNewMessageHooks(self.account, self.igMobile)
