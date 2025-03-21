from script.extra.actions.follow_good_pages.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.follow_good_pages.BrowserFollowGoodPagesEvent import BrowserFollowGoodPagesEvent
import traceback


class FollowGoodPagesContext(InstagramMiddleware):
    ig = None
    strategies = [CanFollowToday]

    def execute(self):
        try:
            self.cant_perform()

            BrowserFollowGoodPagesEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Following Good pages : {str(e)}')
            self.ig.account.add_log(f'Problem Following Good pages : {traceback.format_exc()}')

        return False
