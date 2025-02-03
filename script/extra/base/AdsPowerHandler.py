import requests
from playwright.sync_api import sync_playwright
from script.extra.base.IBrowserHandler import IBrowserHandler
from script.extra.modules.adspower.Adspower import Adspower


class AdsPowerHandler(IBrowserHandler):

    def start_browser(self):
        self.ws_endpoint = Adspower().get_endpoint_url(self.profile_id)
        super().start_browser()

    def cleanup(self):
        super().cleanup()

        try:
            self.account.add_cli('Closing Adspower profile ...')
            Adspower().close_browser(self.profile_id)
        except Exception as e:
            self.account.add_cli(f'Problem Closing Profile : {str(e)}')

