from script.extra.base.IBrowserHandler import IBrowserHandler
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from script.extra.modules.multilogin.Multilogin import Multilogin


class MultiloginHandler(IBrowserHandler):
    profile_id = None
    mlx_url = None

    def start_browser(self):

        self.ws_endpoint = Multilogin().get_endpoint_url(self.profile_id)
        super().start_browser()

    def cleanup(self):
        super().cleanup()

        try:
            self.account.add_cli('Closing MLX profile ...')
            Multilogin().close_browser(self.profile_id)
        except Exception as e:
            self.account.add_cli(f'Problem Closing Profile : {str(e)}')
