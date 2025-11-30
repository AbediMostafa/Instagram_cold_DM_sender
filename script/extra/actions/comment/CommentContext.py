from script.extra.actions.follow.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserCommentEvent import BrowserCommentEvent
import traceback


class CommentContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserCommentEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Commenting on post : {str(e)}')
            self.ig.account.add_log(f'Problem Commenting on post : {traceback.format_exc()}')

        return False
