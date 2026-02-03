from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserChangeBioEvent import BrowserChangeBioEvent
import traceback


class ChangeBioContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserChangeBioEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem changing the bio : {str(e)}')
            self.ig.account.add_log(f'Problem changing the bio : {traceback.format_exc()}')

        return False
