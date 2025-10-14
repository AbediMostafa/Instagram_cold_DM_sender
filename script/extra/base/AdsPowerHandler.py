import requests
from playwright.sync_api import sync_playwright
from script.extra.base.IBrowserHandler import IBrowserHandler
from script.extra.modules.adspower.Adspower import Adspower
from script.extra.modules.adspower.ProfileUpdator import ProfileUpdator
from script.models.Profile import get_next


class AdsPowerHandler(IBrowserHandler):

    def create_profile(self):
        self.account.add_cli('Creating Profile ....')

        creator = ProfileUpdator(self.account)
        creator.call_action('create')

    def change_proxy(self):
        self.account.add_cli('Change profile proxy ....')

        creator = ProfileUpdator(self.account)
        creator.call_action('change_proxy')

    def update_profile(self):
        self.account.add_cli('Updating Profile ....')

        # Get next free profile to update
        profile = get_next()

        updator = ProfileUpdator(self.account, profile)
        updator.call_action('update')

    def delete_profile(self):
        if self.account.profile is None:
            return self.account.add_cli('Account dont have profile to delete ...')

        self.account.add_cli('Deleting Profile ....')
        creator = ProfileUpdator(self.account)
        creator.call_action('delete')

    def start_browser(self):
        self.ws_endpoint = Adspower().get_endpoint_url(self.account.profile.profile_id)
        super().start_browser()

    def cleanup(self):
        super().cleanup()

        if self.account.profile is None:
            return self.account.add_cli('Dont have profile to Close ...')

        try:
            self.account.add_cli('Closing Adspower profile ...')
            response = Adspower().close_browser(self.account.profile.profile_id)
            self.account.add_cli(f'Close adspower status code : {response.status_code}')
            self.account.add_cli(f'Close adspower json : {response.json()}')
        except Exception as e:
            self.account.add_cli(f'Problem Closing Profile : {str(e)}')
