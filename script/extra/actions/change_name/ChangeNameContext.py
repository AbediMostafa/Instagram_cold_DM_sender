from script.extra.actions.change_name.strategies.NameChangedAlready import NameChangedAlready
from script.extra.actions.change_name.strategies.AccountIsOldEnough import AccountIsOldEnough
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.change_name.BrowserChangeNameEvent import BrowserChangeNameEvent
import traceback


class ChangeNameContext(InstagramMiddleware):
    ig = None
    strategies = [NameChangedAlready, AccountIsOldEnough]

    def execute(self):
        try:
            self.cant_perform()

            BrowserChangeNameEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem changing Account name : {str(e)}')
            self.ig.account.add_log(f'Problem changing Account name : {traceback.format_exc()}')

        return False
