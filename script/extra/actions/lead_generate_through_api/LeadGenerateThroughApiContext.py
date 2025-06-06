from script.extra.actions.lead_generate_through_api.strategies.CanGenerateLeadThroughApi import \
    CanGenerateLeadThroughApi
from script.extra.actions.lead_generate_through_api.strategies.HaveEnoughHashtag import HaveEnoughHashtag
from script.extra.actions.lead_generate_through_api.strategies.IsProperServer import IsProperServer
from script.extra.exceptions import CantPerformAction, DontHaveEnoughEntity
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateThroughApiEvent import BrowserLeadGenerateThroughApiEvent
import traceback


class LeadGenerateThroughApiContext(InstagramMiddleware):
    ig = None
    hashtag_count = 3
    strategies = [IsProperServer, CanGenerateLeadThroughApi, HaveEnoughHashtag]

    def execute(self):
        try:
            self.cant_perform()

            BrowserLeadGenerateThroughApiEvent(self.ig).init(self.hashtag_count)

        except CantPerformAction as e:
            return True

        except DontHaveEnoughEntity as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Generating leads Through API : {str(e)}')
            self.ig.account.add_log(f'Problem Generating leads Through API : {traceback.format_exc()}')

        return False
