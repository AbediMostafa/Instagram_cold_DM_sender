from script.extra.actions.follow.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.follow.BrowserFollowEvent import BrowserFollowEvent
import traceback


class FollowContext(InstagramMiddleware):
    ig = None
    strategies = [CanFollowToday]

    def execute(self):
        try:
            self.cant_perform()

            BrowserFollowEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Following leads : {str(e)}')
            self.ig.account.add_log(f'Problem Following leads : {traceback.format_exc()}')

        return False
