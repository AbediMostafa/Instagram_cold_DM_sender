from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.send_dm.strategies.HitTheMaxAllowedDm import HitTheMaxAllowedDm
from script.extra.actions.send_dm.strategies.IsProperServer import IsProperServer
from script.extra.actions.send_dm.strategies.AccountIsOldEnough import AccountIsOldEnough
from script.extra.exceptions import CantPerformAction, IsNotProperServer
import traceback
from .BrowserSendDmWithPostEvent import BrowserSendDmWithPostEvent


class SendDmWithPostContext(InstagramMiddleware):
    ig = None
    strategies = [IsProperServer, HitTheMaxAllowedDm, AccountIsOldEnough]

    def execute(self):
        try:
            self.cant_perform()

            BrowserSendDmWithPostEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except IsNotProperServer as e:
            self.ig.account.add_cli(str(e))
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem sending DM : {str(e)}')
            self.ig.account.add_log(f'Problem sending DM : {traceback.format_exc()}')

        return False
