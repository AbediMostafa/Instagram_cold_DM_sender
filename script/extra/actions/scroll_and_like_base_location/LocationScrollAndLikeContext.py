from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.scroll_and_like_base_location.BrowserLocationScrollAndLikeEvent import BrowserLocationScrollAndLikeEvent
from script.extra.actions.scroll_and_like_base_location.BrowserHashtagScrollAndLikeEvent import BrowserHashtagScrollAndLikeEvent
import traceback
import random


class LocationScrollAndLikeContext(InstagramMiddleware):

    def execute(self):
        try:
            # randomly pick location or hashtag strategy
            strategy = random.choice(['location', 'hashtag'])

            if strategy == 'location':
                self.ig.account.add_cli("Warm-up strategy: Location-based")
                BrowserLocationScrollAndLikeEvent(self.ig).init()
            else:
                self.ig.account.add_cli("Warm-up strategy: Hashtag-based")
                BrowserHashtagScrollAndLikeEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem in location scroll and like: {str(e)}')
            self.ig.account.add_log(f'Problem in location scroll and like: {traceback.format_exc()}')