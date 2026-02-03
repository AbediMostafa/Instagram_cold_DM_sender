from script.extra.actions.make_account_private.strategies.AccountIsPrivateAlready import AccountIsPrivateAlready
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserMakeAccountPrivateEvent import BrowserMakeAccountPrivateEvent
import traceback


class MakeAccountPrivateContext(InstagramMiddleware):
    ig = None
    strategies = [AccountIsPrivateAlready]

    def execute(self):
        try:
            self.cant_perform()

            BrowserMakeAccountPrivateEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem making account public : {str(e)}')
            self.ig.account.add_log(f'Problem making account public : {traceback.format_exc()}')

        return False
