from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadScreenshotEvent import BrowserLeadScreenshotEvent
import traceback


class LeadScreenshotContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()
            self.ig.account.add_cli('Starting lead screenshot module ...')
            BrowserLeadScreenshotEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem taking lead screenshots: {str(e)}')
            self.ig.account.add_log(f'Problem taking lead screenshots: {traceback.format_exc()}')

        return False
