from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .StoryPreparerEvent import StoryPreparerEvent
import traceback


class StoryPreparerContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            StoryPreparerEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem preparing story: {str(e)}')
            self.ig.account.add_log(f'Problem preparing story: {traceback.format_exc()}')

        return False
