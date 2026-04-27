from dotenv import load_dotenv
import os
import requests
import uuid
from datetime import timedelta
from time import sleep
from script.extra.helper import tehran_now
from peewee import OperationalError, fn, JOIN
from script.models.AdsPowerLock import AdsPowerLock
from script.models.Proxy import Proxy
from script.models.Proxy import get_free_proxy
from script.models.AccountHelper import get_storage_state
from script.models.Profile import Profile
from script.extra.exceptions import ProxyStuck

TIME_TO_SLEEP = 400


class ProfileUpdator:
    account = None
    proxy = None
    proxy_obj = None
    profile_name = None
    response_message = None
    response_data = None
    profile = None
    cookies = None
    folder_id = "8972883"
    response = "8972883"
    payload = {
        "name": "",
        "group_id": "",
        "cookie": "",
        "user_proxy_config": {},
        "fingerprint_config": {
            "language_switch": 0,
            "language": ["en-US", "en"],
            "screen_resolution": "random",
            "random_ua": {
                "ua_system_version": ["Windows 10"]
            }
        }
    }

    def __init__(self, account, profile=None):
        self.account = account
        self.profile = profile

    def assign_cookies(self):
        import json

        storage_state = get_storage_state(self.account)
        if not storage_state or "cookies" not in storage_state:
            return None

        cookies = storage_state["cookies"]
        return json.dumps(cookies)

    def get_proxy(self):

        self.proxy_obj = get_free_proxy(self.account)

        return {
            "proxy_soft": "other",
            "proxy_type": "socks5",
            "proxy_host": self.proxy_obj.ip,
            "proxy_port": self.proxy_obj.port,
            "proxy_user": self.proxy_obj.username,
            "proxy_password": self.proxy_obj.password,
        }

    def assign_profile_name(self):
        uid = self.account.id if self.account else str(uuid.uuid4())
        self.profile_name = f"profile_{uid}"
        return self.profile_name

    def create(self):
        self.account.add_cli('Creating account ....')
        try:
            sleep(3)

            cookies = self.assign_cookies()

            if cookies:
                self.payload["cookie"] = self.assign_cookies()

            self.payload["group_id"] = self.folder_id
            self.payload["user_proxy_config"] = self.get_proxy()
            self.payload["name"] = self.assign_profile_name()

            self.send_request() \
                .create_profile_record() \
                .update_account()

        except ProxyStuck:
            raise

        except Exception as e:
            self.account.add_cli(f"Error: {e} | {self.response_message}")
            raise Exception(f"{str(e)} | {self.response_message}")

    def assign_screen_resolution(self):
        import random

        screen_resolutions = [
            # '1280_800',
            # '1280_960',
            '1360_768',
            '1400_900',
            '1440_900',
            '1400_1050',
            '1440_900',
            '1536_864',
        ]
        resolution = random.choice(screen_resolutions)
        print(f'Random resolution: {resolution}')

        self.payload["fingerprint_config"]["screen_resolution"] = resolution

    def update(self):
        self.account.add_cli('Updating account ....')

        try:
            self.payload = {
                'profile_id': self.profile.profile_id,
                "user_proxy_config": self.get_proxy(),
                'cookie': self.assign_cookies(),
                "fingerprint_config": {
                    "language_switch": 0,
                    "language": ["en-US", "en"],
                    "random_ua": {
                        "ua_system_version": ["Windows 10"]
                    }
                }
            }

            self.assign_screen_resolution()

            self.send_request().update_account()

        except Exception as e:
            self.account.add_cli(f"Error: {e} | {self.response_message}")
            raise Exception(f"{str(e)} | {self.response_message}")

    def send_request(self):
        url = "http://local.adspower.net:50325/api/v2/browser-profile/create"
        max_retries = 5
        retry_delay = 2

        for attempt in range(1, max_retries):
            self.response = requests.post(url, json=self.payload, verify=False)

            try:
                json_response = self.response.json()
                self.account.add_cli(f"Create response (Attempt {attempt})")
                self.account.add_cli(json_response)
            except Exception:
                raise Exception(f"Invalid response: {self.response.text}")

            self.response_message = json_response.get("msg", "")
            self.response_data = json_response.get("data", {})

            if json_response.get("code") == -1 and "Too many request" in self.response_message:
                if attempt < max_retries:
                    sleep(retry_delay)
                    continue
                else:
                    raise Exception("Maximum retry attempts reached: Too many requests per second")
            else:
                break

        return self

    def update_request(self):
        url = "http://local.adspower.net:50325/api/v2/browser-profile/update"
        self.response = requests.post(url, json=self.payload, verify=False)

        try:
            json_response = self.response.json()
            self.account.add_cli("Create response")
            self.account.add_cli(json_response)

        except Exception:
            raise Exception(f"Invalid response: {self.response.text}")

        self.response_message = json_response.get("msg", "")
        self.response_data = json_response.get("data", {})

        return self

    def create_profile_record(self):
        self.profile = Profile.create(
            title=self.profile_name,
            folder=self.folder_id,
            profile_id=self.response_data.get('profile_id'),
            proxy=self.proxy_obj if self.proxy_obj else None
        )
        return self

    def update_account(self):
        self.account.profile = self.profile
        self.account.save()
        return self

    def delete(self):
        self.account.add_cli(f'Deleting Profile {self.account.profile.profile_id}')

        payload = {
            "user_ids": [self.account.profile.profile_id],
        }

        url = "http://local.adspower.net:50325/api/v1/user/delete"
        response = requests.post(url, json=payload, verify=False)

        if not response.ok:
            raise Exception(f"Error while deleting profile: {response.text}")
        return self

    def call_action(self, action):
        '''
        It's possible for multiple account to call account creation API,
        so we need to call the API through a lock system
        '''
        while True:
            try:
                lock_row = AdsPowerLock.select().first()
                last_executed_at = lock_row.last_executed_at

                added_time = last_executed_at + timedelta(milliseconds=TIME_TO_SLEEP)
                wait_seconds = (added_time - tehran_now()).total_seconds()

                self.account.add_cli(f'wait seconds     : {wait_seconds}')

                if wait_seconds > 0:
                    self.account.add_cli(f'We hav to wait {wait_seconds} seconds ...')
                    sleep(0.5)
                    continue

                getattr(self, action)()

                lock_row.last_executed_at = tehran_now()
                lock_row.save()
                break

            except OperationalError:
                print('Database is busy, waiting .5 seconds ...')
                sleep(0.5)

    def close_browser(self):
        url = f'http://local.adspower.net:50325/api/v1/browser/stop?user_id={self.account.profile.profile_id}'
        requests.get(url)

    def check_account(self):

        if self.account.profile is None:
            return self.account.add_cli(f"Previous account didnt have a profile")

        try:
            url = f"http://local.adspower.net:50325/api/v1/browser/active?user_id={self.account.profile.profile_id}"
            response = requests.get(url, verify=False)
            status = response.json().get('data').get('status')

            self.account.add_cli(f"Previous profile is : {status}")

            if status == 'Active':
                self.account.add_cli(f"Closing and deleting previous profile")

                self.call_action('close_browser')
                self.call_action('delete')

        except Exception as e:
            self.account.add_cli(f"Error checking previous account: {e}")

    def change_proxy(self):
        self.get_proxy(type='private_residential')
        self.payload["profile_id"] = self.account.profile.profile_id
        self.payload["group_id"] = self.folder_id
        self.payload["user_proxy_config"] = self.proxy
        self.update_request()
