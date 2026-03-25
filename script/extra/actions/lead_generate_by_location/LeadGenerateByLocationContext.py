from script.extra.actions.lead_generate_by_followers.strategies.CanGenerateLeadByFollowers import \
    CanGenerateLeadByFollowers

from script.extra.actions.lead_generate_by_followers.strategies.IsProperServer import IsProperServer
from script.extra.exceptions import IsNotProperServer, CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateByLocationEvent import BrowserLeadGenerateByLocationEvent
import traceback


class LeadGenerateByLocationContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:

            self.cant_perform()
            self.ig.account.add_cli("Generating lead by Location ... ")
            BrowserLeadGenerateByLocationEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem Generating leads Through Location : {str(e)}')
            self.ig.account.add_log(f'Problem Generating leads Through Location : {traceback.format_exc()}')

        return False
