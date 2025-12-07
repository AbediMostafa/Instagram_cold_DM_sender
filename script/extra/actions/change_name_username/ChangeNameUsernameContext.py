from script.extra.actions.change_name.strategies.NameChangedAlready import NameChangedAlready
from script.extra.actions.change_name.strategies.AccountIsOldEnough import AccountIsOldEnough
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserChangeNameUsernameEvent import BrowserChangeNameUsernameEvent

import traceback


class ChangeNameUsernameContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserChangeNameUsernameEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem changing Account name and username : {str(e)}')
            self.ig.account.add_log(f'Problem changing Account name and username : {traceback.format_exc()}')

        return False
