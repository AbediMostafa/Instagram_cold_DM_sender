from script.extra.exceptions import IsNotProperServer, CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import traceback


class GetRequestsPayloadAndHeaderContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()
            self.ig.account.add_cli("Generating lead by followers")
            BrowserLeadGenerateByFollowersEvent(self.ig).init(self.lead_source_count)

        except IsNotProperServer as e:
            self.ig.account.add_cli(str(e))
            return True

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Generating leads Through Followers : {str(e)}')
            self.ig.account.add_log(f'Problem Generating leads Through Followers : {traceback.format_exc()}')

        return False

