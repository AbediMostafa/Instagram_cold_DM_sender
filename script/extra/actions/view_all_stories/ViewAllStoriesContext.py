from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserViewAllStoriesEvent import BrowserViewAllStoriesEvent
import traceback


class ViewAllStoriesContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            ئشدخ(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem viewing all stories: {str(e)}')
            self.ig.account.add_log(f'Problem viewing all stories: {traceback.format_exc()}')

        return False
