from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserPostInsightsEvent import BrowserPostInsightsEvent
import traceback


class PostInsightsContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserPostInsightsEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem collecting post insights: {str(e)}')
            self.ig.account.add_log(f'Problem collecting post insights: {traceback.format_exc()}')

        return False
