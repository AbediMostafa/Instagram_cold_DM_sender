import os
from dotenv import load_dotenv
import requests
from script.models.Setting import Setting
import hashlib

load_dotenv()


class Requests:

    def __init__(self):
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

    def request(self, _type, url, data=None):

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Setting.get_value('mlx_token')}"
        }

        def send_request():
            return requests.get(url, headers=headers) if _type == 'get' else requests.post(url, headers=headers,
                                                                                           data=data)

        resp = send_request()

        if resp.status_code == 401:
            resp_json = resp.json()
            error_code = resp_json['status']['error_code']

            if error_code == "EXPIRED_JWT_TOKEN" or error_code == "UNAUTHORIZED_REQUEST":
                self.renew_token()
                return send_request()

        if resp.status_code != 200:
            raise Exception(f"Error while Sending Multilogin {_type} Request : {resp.text}")

        return resp

    def get_mlx_endpoint_url(self, profile_id):

        resp = self.request(
            "get",
            f"https://launcher.mlx.yt:45001/api/v2/profile/f/{os.getenv('MLX_FOLDER_ID')}/p/{profile_id}/start?automation_type=playwright&headless_mode=false"
        )

        resp_json = resp.json()
        port = resp_json["data"]["port"]
        url = f"http://127.0.0.1:{port}"

        return url

    def close_mlx_profile(self, profile_id):
        try:
            self.request('get', f"https://launcher.mlx.yt:45001/api/v1/profile/stop/p/{profile_id}")

        except Exception as e:
            print(f"Error while closing profile: {str(e)}")
