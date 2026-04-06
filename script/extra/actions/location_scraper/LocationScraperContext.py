from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLocationScraperEvent import BrowserLocationScraperEvent
import traceback


class LocationScraperContext(InstagramMiddleware):
    ig = None

    def execute(self):
        try:
            self.ig.account.add_cli("Scraping locations ...")
            BrowserLocationScraperEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem scraping locations: {str(e)}')
            self.ig.account.add_log(f'Problem scraping locations: {traceback.format_exc()}')

        return False
