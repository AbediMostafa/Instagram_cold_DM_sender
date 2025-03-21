from script.extra.actions.lead_generate_by_followers.strategies.CanGenerateLeadByFollowers import \
    CanGenerateLeadByFollowers
from script.extra.actions.lead_generate_by_followers.strategies.IsProperServer import IsProperServer
from script.extra.exceptions import IsNotProperServer, CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateByFollowersEvent import BrowserLeadGenerateByFollowersEvent
import traceback


class LeadGenerateByFollowersContext(InstagramMiddleware):
    ig = None
    lead_source_count = 1
    strategies = [CanGenerateLeadByFollowers]

    def execute(self):
        try:
            self.cant_perform()

            BrowserLeadGenerateByFollowersEvent(self.ig).init(self.lead_source_count)

        except IsNotProperServer as e:
            return True

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Generating leads Through Followers : {str(e)}')
            self.ig.account.add_log(f'Problem Generating leads Through Followers : {traceback.format_exc()}')

        return False

