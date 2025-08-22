from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.get_lead_pk.BrowserGetLeadPkEvent import BrowserGetLeadPkEvent
import traceback


class GetLeadPkContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserGetLeadPkEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem getting lead pk : {str(e)}')
            self.ig.account.add_log(f'Problem getting lead pk : {traceback.format_exc()}')

        return False
