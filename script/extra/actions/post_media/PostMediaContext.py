from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserPostMediaEvent import BrowserPostMediaEvent
import traceback


class PostMediaContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserPostMediaEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem posting image from folder : {str(e)}')
            self.ig.account.add_log(f'Problem posting image from folder : {traceback.format_exc()}')

        return False
