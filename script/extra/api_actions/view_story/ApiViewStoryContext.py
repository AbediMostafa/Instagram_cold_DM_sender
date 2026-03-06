from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserApiViewStoryEvent import BrowserApiViewStoryEvent
import traceback


class ApiViewStoryContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserApiViewStoryEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem viewing story via API: {str(e)}')
            self.ig.account.add_log(f'Problem viewing story via API: {traceback.format_exc()}')

        return False
