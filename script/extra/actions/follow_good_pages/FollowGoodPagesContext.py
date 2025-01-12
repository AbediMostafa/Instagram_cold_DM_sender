from script.extra.actions.follow_good_pages.strategies.CanFollowToday import CanFollowToday
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.follow_good_pages.BrowserFollowGoodPagesEvent import BrowserFollowGoodPagesEvent


class FollowGoodPagesContext(InstagramMiddleware):
    ig = None
    strategies = [CanFollowToday]

    def execute(self):

        if self.cant_perform():
            return False

    def cant_perform(self):
        try:
            for strategy in self.strategies:
                strategy(self.ig.account).can()

        except CantPerformAction as e:
            self.ig.account.add_cli(str(e))
            return True

        except Exception as e:
            self.ig.account.add_cli(str(e))

        return False
