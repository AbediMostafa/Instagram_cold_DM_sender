from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.send_dm.strategies.HitTheMaxAllowedDm import HitTheMaxAllowedDm
from script.extra.exceptions import CantPerformAction
import traceback
from .BrowserSendDmEvent import BrowserSendDmEvent


class SendDmContext(InstagramMiddleware):
    ig = None
    strategies = [HitTheMaxAllowedDm]

    def execute(self):
        try:
            self.cant_perform()

            BrowserSendDmEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem sending DM : {str(e)}')
            self.ig.account.add_log(f'Problem sending DM : {traceback.format_exc()}')

        return False


