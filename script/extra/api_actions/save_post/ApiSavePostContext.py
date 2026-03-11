from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserApiSavePostEvent import BrowserApiSavePostEvent
import traceback


class ApiSavePostContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserApiSavePostEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem saving post via API: {str(e)}')
            self.ig.account.add_log(f'Problem saving post via API: {traceback.format_exc()}')

        return False
