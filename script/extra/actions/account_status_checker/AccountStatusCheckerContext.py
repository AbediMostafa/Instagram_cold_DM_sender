from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserAccountStatusCheckerEvent import BrowserAccountStatusCheckerEvent
import traceback


class AccountStatusCheckerContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserAccountStatusCheckerEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem checking account status: {str(e)}')
            self.ig.account.add_log(f'Problem checking account status: {traceback.format_exc()}')

        return False