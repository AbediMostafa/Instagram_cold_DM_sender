from script.extra.actions.follow.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction, SuccessfulLogin
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.follow.BrowserFollowEvent import BrowserFollowEvent
from script.extra.actions.login.BrowserLoginEvent import BrowserLoginEvent
import traceback


class LoginContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserLoginEvent(self.ig).init()

        except SuccessfulLogin:
            self.ig.account.add_cli('Successfully logged in')
            return True

        except CantPerformAction as e:
            return True

        return False
