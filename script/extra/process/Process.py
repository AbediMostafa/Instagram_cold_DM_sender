from script.extra.instagram.InstagramMobile import InstagramMobile
from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
from script.extra.hooks.RecordLastActivityHook import RecordLastActivityHook
from script.extra.hooks.CheckForLastLoginHook import CheckForLastLoginHook
from script.extra.hooks.CheckForWarningsHook import CheckForWarningsHook
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy
from script.models.AccountHelper import get_next_account


class Process:
    account = None
    name_command = None
    username_command = None
    avatar_command = None
    ig = None
    follow = None

    def start(self):

        try:
            self.account = get_next_account()
            self.ig = InstagramMobile(self.account)

            should_stop = self.before_process_hooks()  # Execute hooks once and store the result

            if should_stop:
                return  # Exit

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
            if not should_stop:  # Only record last activity if hooks did not stop the process
                RecordLastActivityHook(self.account)

    def do_process(self):
        self.account.set_state('processing', 'app_state')
        self.ig.log_in()
        self.account.set_state('active')

        HowManyEventsCanHandleStrategy(self.account, self.ig).run()

    def before_process_hooks(self):
        if CheckForWarningsHook(self.account).last_warning_has_not_expired():
            return True

        if CheckForLastLoginHook(self.account).next_login_not_reached():
            return True

        return False

    def after_process_hooks(self):
        CheckNewMessageHooks(self.account, self.ig)
