from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserSwitchToCreatorEvent import BrowserSwitchToCreatorEvent
import traceback


class SwitchToCreatorContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserSwitchToCreatorEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'[SwitchToCreator] Problem: {str(e)}')
            self.ig.account.add_log(f'[SwitchToCreator] Problem: {traceback.format_exc()}')

        return False
