from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserCommentOnOthersPostEvent import BrowserCommentOnOthersPostEvent
import traceback


class CommentOnOthersPostContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserCommentOnOthersPostEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem commenting on others post: {str(e)}')
            self.ig.account.add_log(f'Problem commenting on others post: {traceback.format_exc()}')

        return False