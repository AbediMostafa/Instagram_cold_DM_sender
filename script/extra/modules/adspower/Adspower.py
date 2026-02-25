import requests
import os
from dotenv import load_dotenv

load_dotenv()


class Adspower:
    """
    AdsPower Browser Handler

    Set ADSPOWER_HEADLESS in .env file:
    - ADSPOWER_HEADLESS=true  -> No GUI (~150MB RAM per browser)
    - ADSPOWER_HEADLESS=false -> With GUI (~500MB RAM per browser)

    With 40 threads:
    - Headed:   ~20GB RAM
    - Headless: ~6GB RAM -> Can scale to 60-80 threads
    """

    @staticmethod
    def is_headless():
        """Read headless setting from environment variable"""
        value = os.getenv('ADSPOWER_HEADLESS', 'false').lower()
        return value in ('true', '1', 'yes')

    def get_endpoint_url(self, account):

        profile_id = account.profile.profile_id
        headless = self.is_headless()

        headless_param = '&headless=1' if headless else ''

        url = f'http://local.adspower.net:50325/api/v1/browser/start?user_id={profile_id}&ip_tab=0{headless_param}'

        mode_text = "Headless" if headless else "Headed"
        account.add_cli(f'Starting browser ({mode_text})...')

        response = requests.get(url)

        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('code') == 0 and res_data.get('data', {}).get('ws', {}).get('puppeteer'):
                ws_endpoint = res_data['data']['ws']['puppeteer']
                return ws_endpoint

        account.add_cli(response.text)
        raise Exception("Failed to start AdsPower browser.")

    def close_browser(self, profile_id):
        return requests.get(
            f'http://local.adspower.net:50325/api/v1/browser/stop?user_id={profile_id}')