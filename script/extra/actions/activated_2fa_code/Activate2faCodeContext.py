from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.activated_2fa_code.BrowserActivate2faCodeEvent import BrowserActivate2faCodeEvent
from script.extra.exceptions import CantPerformAction
from script.extra.actions.activated_2fa_code.strategies.TwoFactorActivatedAlready import TwoFactorActivatedAlready
import traceback


class Activate2faCodeContext(InstagramMiddleware):
    ig = None
    strategies =[TwoFactorActivatedAlready]

    def execute(self):
        try:
            self.cant_perform()

            BrowserActivate2faCodeEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Activating 2fa code: {str(e)}')
            self.ig.account.add_log(f'Problem Activating 2fa code: {traceback.format_exc()}')

        return False