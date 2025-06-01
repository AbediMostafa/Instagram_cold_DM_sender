from script.extra.actions.lead_generate_following_other_leads.strategies.CanFollowLeadToday import CanFollowLeadToday
from script.extra.actions.lead_generate_following_other_leads.strategies.IsProperServer import IsProperServer
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateFollowingOtherLeadsEvent import BrowserLeadGenerateFollowingOtherLeadsEvent


class LeadGenerateFollowingOtherLeadsContext(InstagramMiddleware):
    ig = None
    strategies = [IsProperServer, CanFollowLeadToday]

    def execute(self):

        if self.cant_perform():
            return False

        BrowserLeadGenerateFollowingOtherLeadsEvent(self.ig).init()

    def cant_perform(self):
        try:
            for strategy in self.strategies:
                strategy(self.ig.account).can()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(str(e))

        return False
