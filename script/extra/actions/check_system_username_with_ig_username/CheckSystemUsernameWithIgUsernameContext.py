from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.check_system_username_with_ig_username.BrowserCheckSystemUsernameWithIgUsernameEvent import BrowserCheckSystemUsernameWithIgUsernameEvent
import traceback


class CheckSystemUsernameWithIgUsernameContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserCheckSystemUsernameWithIgUsernameEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Deleting initial posts : {str(e)}')
            self.ig.account.add_log(f'Problem Deleting initial posts : {traceback.format_exc()}')

        return False
