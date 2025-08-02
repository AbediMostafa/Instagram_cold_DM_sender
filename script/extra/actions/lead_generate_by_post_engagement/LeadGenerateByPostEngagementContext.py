from script.extra.actions.lead_generate_by_post_engagement.strategies.CanGenerateLeadByPostEngagement import \
    CanGenerateLeadByPostEngagement

from script.extra.actions.lead_generate_by_post_engagement.strategies.IsProperServer import IsProperServer
from script.extra.exceptions import IsNotProperServer, CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateByPostEngagementEvent import BrowserLeadGenerateByPostEngagementEvent
import traceback


class LeadGenerateByPostEngagementContext(InstagramMiddleware):
    ig = None
    strategies = [IsProperServer, CanGenerateLeadByPostEngagement]

    def execute(self):
        try:
            self.cant_perform()
            self.ig.account.add_cli("Generating lead by Hashtags")

            BrowserLeadGenerateByPostEngagementEvent(self.ig).init()

        except IsNotProperServer as e:
            return True

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Generating leads by post engagement : {str(e)}')
            self.ig.account.add_log(f'Problem Generating leads by post engagement : {traceback.format_exc()}')

        return False
