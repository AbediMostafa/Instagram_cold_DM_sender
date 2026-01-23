from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.reels_average_extractor.BrowserReelsAverageExtractorEvent import BrowserReelsAverageExtractorEvent
from script.extra.exceptions import CantPerformAction
import traceback


class ReelsAverageExtractor(InstagramMiddleware):
    ig = None
    strategies =[]

    def execute(self):
        try:
            self.cant_perform()

            BrowserReelsAverageExtractorEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem extracting reels average: {str(e)}')
            self.ig.account.add_log(f'Problem extracting reels average: {traceback.format_exc()}')

        return False