from script.extra.actions.lead_generate_by_page_engagement.strategies.CanGenerateLeadByPageEngagement import \
    CanGenerateLeadByPageEngagement
from script.extra.exceptions import IsNotProperServer, CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateByPageEngagementEvent import BrowserLeadGenerateByPageEngagementEvent
import traceback


class LeadGenerateByPageEngagementContext(InstagramMiddleware):
    ig = None
    strategies = [CanGenerateLeadByPageEngagement]

    def execute(self):
        try:
            self.cant_perform()

            BrowserLeadGenerateByPageEngagementEvent(self.ig).init()

        except IsNotProperServer as e:
            return True

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Generating leads by engagement : {str(e)}')
            self.ig.account.add_log(f'Problem Generating leads by engagement : {traceback.format_exc()}')

        return False
