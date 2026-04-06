from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserFollowPagesViaLocationEvent import BrowserFollowPagesViaLocationEvent
import traceback


class FollowPagesViaLocationContext(InstagramMiddleware):

    def execute(self):
        try:
            BrowserFollowPagesViaLocationEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem in follow pages via location: {str(e)}')
            self.ig.account.add_log(f'Problem in follow pages via location: {traceback.format_exc()}')
