import requests
from playwright.sync_api import sync_playwright
from script.extra.base.IBrowserHandler import IBrowserHandler
from script.extra.modules.adspower.Adspower import Adspower
from script.extra.modules.adspower.ProfileUpdator import ProfileUpdator
from script.models.Profile import get_next
from time import sleep


class AdsPowerHandler(IBrowserHandler):
    user_id_not_open_message = 'User_id is not open'
    proxy = None

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
        updator.update()

        # Store proxy reference for later use in API requests
        self.proxy = updator.proxy_obj
        if self.proxy:
            self.account.add_cli(f'[PROXY] Stored proxy: {self.proxy.get_proxy_identifier()}')

    def delete_profile(self):
        if self.account.profile is None:
            return self.account.add_cli('Account dont have profile to delete ...')

        self.account.add_cli('Deleting Profile ....')
        creator = ProfileUpdator(self.account)
        creator.call_action('delete')

    def start_browser(self):
        self.ws_endpoint = Adspower().get_endpoint_url(self.account)
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

    def delete_adspower_cache(self):
        import shutil
        import os

        cache_base = r'C:\.ADSPOWER_GLOBAL\cache'
        profile_id = self.account.profile.profile_id

        if not os.path.isdir(cache_base):
            print('[CACHE] Cache base folder not found')
            return

        deleted = False

        for folder in os.listdir(cache_base):
            # match: profile_id_*
            if folder.startswith(f'{profile_id}_'):
                full_path = os.path.join(cache_base, folder)

                try:
                    shutil.rmtree(full_path)
                    print(f'[CACHE] Deleted cache folder: {folder}')
                    deleted = True
                except Exception as e:
                    print(f'[CACHE] Failed to delete {folder}: {e}')

        if not deleted:
            print(f'[CACHE] No cache folder found for profile {profile_id}')