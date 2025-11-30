from script.extra.actions.follow.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLikeAndCommentEvent import BrowserLikeAndCommentEvent
import traceback


class LikeAndCommentContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserLikeAndCommentEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Commenting and liking the post : {str(e)}')
            self.ig.account.add_log(f'Problem Commenting and liking the post : {traceback.format_exc()}')

        return False
