from script.extra.actions.follow.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.get_account_username.BrowserGetAccountUsernameEvent import BrowserGetAccountUsernameEvent
import traceback


class GetAccountUsernameContext(InstagramMiddleware):
    ig = None
    strategies = [CanFollowToday]

    def execute(self):
        try:
            BrowserGetAccountUsernameEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Getting account username : {str(e)}')
            self.ig.account.add_log(f'Problem Getting account username : {traceback.format_exc()}')

        return False
