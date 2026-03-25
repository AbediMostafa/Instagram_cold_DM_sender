from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLocationExtractorEvent import BrowserLocationExtractorEvent
import traceback


class LocationExtractorContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:

            self.cant_perform()

            BrowserLocationExtractorEvent(self.ig).init()

            self.ig.account.add_cli("Location extraction completed")

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem extracting locations : {str(e)}')
            self.ig.account.add_log(f'Problem extracting locations : {traceback.format_exc()}')

        return False