import requests


class Adspower:

    def get_endpoint_url(self, profile_id):
        response = requests.get(
            f'http://local.adspower.net:50325/api/v1/browser/start?user_id={profile_id}&ip_tab=0')

        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('code') == 0 and res_data.get('data', {}).get('ws', {}).get('puppeteer'):
                ws_endpoint = res_data['data']['ws']['puppeteer']

                return ws_endpoint

        print(response.text)
        raise Exception("Failed to start AdsPower browser.")

    def close_browser(self, profile_id):
        response = requests.get(
            f'http://local.adspower.net:50325/api/v1/browser/stop?user_id={profile_id}')
