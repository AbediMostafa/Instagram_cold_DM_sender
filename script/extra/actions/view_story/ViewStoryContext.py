from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserViewStoryEvent import BrowserViewStoryEvent
import traceback


class ViewStoryContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserViewStoryEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem viewing story: {str(e)}')
            self.ig.account.add_log(f'Problem viewing story: {traceback.format_exc()}')

        return False
