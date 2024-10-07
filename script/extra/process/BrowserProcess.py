from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.models.AccountHelper import get_next_account


class BrowserProcess:
    account = None
    name_command = None
    username_command = None
    avatar_command = None
    ig = None
    follow = None

    def start(self):
        try:
            # self.account = Account.get_by_id(237)
            self.account = get_next_account()
            self.ig = BasePlaywright(self.account)
            self.account.set_state('processing', 'app_state')
            self.do_process()
        # self.after_process_hooks()

        except Exception as e:
            pass
        #
        finally:
            self.account.set_state('idle', 'app_state')
            if self.ig:
                self.ig.cleanup()

    def do_process(self):
        HowManyEventsCanHandleStrategy(self.ig).run()

    def after_process_hooks(self):
        CheckNewMessageHooks(self.account, self.ig)
