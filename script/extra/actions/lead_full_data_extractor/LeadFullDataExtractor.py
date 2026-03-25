from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadFullDataExtractorEvent import BrowserLeadFullDataExtractorEvent
from script.extra.exceptions import CantPerformAction
import traceback


class LeadFullDataExtractor(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserLeadFullDataExtractorEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem extracting lead profile: {str(e)}')
            self.ig.account.add_log(f'Problem extracting lead profile: {traceback.format_exc()}')

        return False
