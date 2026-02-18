from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserSavePostEvent import BrowserSavePostEvent
import traceback


class SavePostContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserSavePostEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem saving post: {str(e)}')
            self.ig.account.add_log(f'Problem saving post: {traceback.format_exc()}')

        return False
