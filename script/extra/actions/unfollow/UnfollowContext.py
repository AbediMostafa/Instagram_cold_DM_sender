from script.extra.actions.unfollow.strategies.CanUnfollowToday import CanUnfollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.unfollow.BrowserUnfollowEvent import BrowserUnfollowEvent
import traceback


class UnfollowContext(InstagramMiddleware):
    ig = None
    strategies = [CanUnfollowToday]

    def execute(self):
        try:
            self.cant_perform()

            BrowserUnfollowEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem performing unfollow : {str(e)}')
            self.ig.account.add_log(f'Problem performing unfollow : {traceback.format_exc()}')

        return False
