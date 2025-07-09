import requests
from playwright.sync_api import sync_playwright
from script.extra.base.IBrowserHandler import IBrowserHandler
from script.extra.modules.adspower.Adspower import Adspower
from script.extra.modules.adspower.ProfileCreator import ProfileCreator


class AdsPowerHandler(IBrowserHandler):

    def create_profile(self):
        self.account.add_cli('Creating Profile ....')

        creator = ProfileCreator(self.account)
        creator.call_action('create')

    def delete_profile(self):
        self.account.add_cli('Deleting Profile ....')
        creator = ProfileCreator(self.account)
        creator.call_action('delete')

    def start_browser(self):
        self.ws_endpoint = Adspower().get_endpoint_url(self.account.profile.profile_id)
        super().start_browser()

    def cleanup(self):
        super().cleanup()

        try:
            self.account.add_cli('Closing Adspower profile ...')
            Adspower().close_browser(self.account.profile.profile_id)
        except Exception as e:
            self.account.add_cli(f'Problem Closing Profile : {str(e)}')
