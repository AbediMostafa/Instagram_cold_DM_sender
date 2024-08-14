from script.extra.instagram.InstagramMobile import InstagramMobile
from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy
from script.extra.instagram.Instagram import Instagram


class Process:
    account = None
    name_command = None
    username_command = None
    avatar_command = None
    ig = None
    ig = None
    follow = None

    def start(self, account):
        try:
            self.account = account
            self.ig = Instagram(self.account)
            self.account.set_state('processing', 'app_state')
            self.ig.go_to_instagram().log_in()

            self.account.set_state('active')
            self.do_process()
            self.after_process_hooks()

        except Exception as e:
            self.account.add_cli(str(e))
            if 'user with that username already exists' in str(e) or "username isn't available" in str(
                    e) or 'Enter a name under 30 characters' in str(
                e) or "You can't end your username with a period" in str(e):
                pass

        finally:
            self.account.set_state('idle', 'app_state')

    def do_process(self):
        HowManyEventsCanHandleStrategy(self.account, self.ig).run()

    def after_process_hooks(self):
        CheckNewMessageHooks(self.account, self.ig)









