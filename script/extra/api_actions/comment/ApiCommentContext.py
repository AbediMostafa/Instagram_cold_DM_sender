from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserApiCommentEvent import BrowserApiCommentEvent
import traceback


class ApiCommentContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserApiCommentEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem with API comment: {str(e)}')
            self.ig.account.add_log(f'Problem with API comment: {traceback.format_exc()}')

        return False
