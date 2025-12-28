from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.lead_profile_extractor.BrowserLeadProfileExtractorEvent import BrowserLeadProfileExtractorEvent
from script.extra.exceptions import CantPerformAction
import traceback


class LeadProfileExtractor(InstagramMiddleware):
    ig = None
    strategies =[]

    def execute(self):
        try:
            self.cant_perform()

            BrowserLeadProfileExtractorEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem extracting lead profile: {str(e)}')
            self.ig.account.add_log(f'Problem extracting lead profile: {traceback.format_exc()}')

        return False