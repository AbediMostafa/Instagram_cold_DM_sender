from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserApiCommentAndReplyEvent import BrowserApiCommentAndReplyEvent
import traceback


class ApiCommentAndReplyContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserApiCommentAndReplyEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem with API comment_and_reply: {str(e)}')
            self.ig.account.add_log(f'Problem with API comment_and_reply: {traceback.format_exc()}')

        return False
