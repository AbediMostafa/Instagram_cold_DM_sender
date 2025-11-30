import requests
from playwright.sync_api import sync_playwright
from script.extra.base.IBrowserHandler import IBrowserHandler
from script.extra.modules.adspower.Adspower import Adspower
from script.extra.modules.adspower.ProfileUpdator import ProfileUpdator
from script.models.Profile import get_next
from time import sleep


class AdsPowerHandler(IBrowserHandler):
    user_id_not_open_message = 'User_id is not open'

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
            closing_count = 1
            response = self.close_adspower(closing_count)

            while response['code'] == -1:

                if response['msg'] == self.user_id_not_open_message:
                    break

                self.account.add_cli(f'Attempt {closing_count} failed to close the profile ...')

                sleep(closing_count)
                closing_count += 1

                response = self.close_adspower(closing_count)

        except Exception as e:
            self.account.add_cli(f'Problem Closing Profile : {str(e)}')

    def close_adspower(self, closing_count):
        self.account.add_cli(f'Closing Adspower profile for {closing_count} ...')
        response = Adspower().close_browser(self.account.profile.profile_id)
        json_response = response.json()
        self.account.add_cli(f'Close adspower json : {json_response}')
        return json_response
