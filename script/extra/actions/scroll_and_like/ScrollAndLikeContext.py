from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.scroll_and_like.BrowserScrollAndLikeEvent import BrowserScrollAndLikeEvent
import traceback


class ScrollAndLikeContext(InstagramMiddleware):

    def execute(self):
        try:
            # Initialize and execute the email registration event
            BrowserScrollAndLikeEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem sending DM : {str(e)}')
            self.ig.account.add_log(f'Problem sending DM : {traceback.format_exc()}')
