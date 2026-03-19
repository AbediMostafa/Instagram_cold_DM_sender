from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserUploadPostConnectEvent import BrowserUploadPostConnectEvent
import traceback


class UploadPostConnectContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BrowserUploadPostConnectEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'[UploadPost] Problem connecting: {str(e)}')
            self.ig.account.add_log(f'[UploadPost] Problem connecting: {traceback.format_exc()}')

        return False