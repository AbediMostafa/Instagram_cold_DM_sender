import requests
from playwright.sync_api import sync_playwright
from script.extra.base.IBrowserHandler import IBrowserHandler
from script.extra.modules.adspower.Adspower import Adspower
from time import sleep
from script.extra.helper import add_cli


class AdsPowerHandler(IBrowserHandler):
    user_id_not_open_message = 'User_id is not open'

    def start_browser(self):

        response = requests.get(
            f'http://local.adspower.net:50325/api/v1/browser/start?user_id={self.profile_id}&ip_tab=0')

        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('code') == 0 and res_data.get('data', {}).get('ws', {}).get('puppeteer'):
                self.ws_endpoint = res_data['data']['ws']['puppeteer']
                return super().start_browser()

        add_cli(response.text, self.account)
        raise Exception("Failed to start AdsPower browser.")

    def cleanup(self):
        super().cleanup()

        try:
            closing_count = 1
            response = self.close_adspower(closing_count)

            while response['code'] == -1:

                if response['msg'] == self.user_id_not_open_message:
                    break

                add_cli(f'Attempt {closing_count} failed to close the profile ...', self.account)

                sleep(closing_count)
                closing_count += 1

                response = self.close_adspower(closing_count)

        except Exception as e:
            add_cli(f'Problem Closing Profile : {str(e)}', self.account)

    def close_adspower(self, closing_count):
        add_cli(f'Closing Adspower profile for {closing_count} ...', self.account)
        response = Adspower().close_browser(self.profile_id)
        json_response = response.json()
        add_cli(f'Close adspower json : {json_response}', self.account)
        return json_response
