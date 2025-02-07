import os
from dotenv import load_dotenv
import requests
from script.models.Setting import Setting
import hashlib


load_dotenv()


class Multilogin:

    def __init__(self):
        Setting.set_value('mlx_lock', False)
        pass

    def renew_token(self):

        if Setting.get_value('mlx_lock') == 'True':
            return True

        Setting.set_value('mlx_lock', True)

        payload = {
            "email": os.getenv('MLX_USERNAME'),
            "password": hashlib.md5(os.getenv('MLX_PASSWORD').encode()).hexdigest(),
        }

        r = requests.post(f"{os.getenv('MLX_BASE')}/user/signin", json=payload)

        if r.status_code != 200:
            raise Exception(f"Error during login: {r.text}")

        else:
            response = r.json()["data"]
            Setting.set_value('mlx_token', response["token"])

        Setting.set_value('mlx_lock', False)

    def get_headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Setting.get_value('mlx_token')}"
        }

    def send_request(self, _type, url, data=None):
        return requests.get(url, headers=self.get_headers()) if _type == 'get' else\
            requests.post(url, data=data)

    def request(self, _type, url, data=None):

        resp = self.send_request(_type, url, data)

        if resp.status_code == 401:
            self.renew_token()
            return self.send_request(_type, url, data)

        if resp.status_code != 200:
            raise Exception(f"Error while Sending Multilogin {_type} Request : {resp.text}")

        return resp

    def get_endpoint_url(self, profile_id):

        resp = self.request(
            "get",
            f"https://launcher.mlx.yt:45001/api/v2/profile/f/{os.getenv('MLX_FOLDER_ID')}/p/{profile_id}/start?automation_type=playwright&headless_mode=false"
        )

        resp_json = resp.json()
        port = resp_json["data"]["port"]
        url = f"http://127.0.0.1:{port}"

        return url

    def close_browser(self, profile_id):
        self.request('get', f"https://launcher.mlx.yt:45001/api/v1/profile/stop/p/{profile_id}")
