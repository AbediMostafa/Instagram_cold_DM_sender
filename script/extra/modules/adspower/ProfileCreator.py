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
from script.models.AccountHelper import get_storage_state
from script.models.Profile import Profile

TIME_TO_SLEEP = 3


class ProfileCreator:
    account = None
    proxy = None
    proxy_obj = None
    profile_name = None
    response_message = None
    response_data = None
    profile = None
    cookies = None
    folder_id = "5780347"
    response = "5780347"
    payload = {
        "name": "",
        "group_id": "",
        "cookie": "",
        "user_proxy_config": {},
        "fingerprint_config": {
            "language": ["en-US", "en"],
            "language_switch": 0,
            "screen_resolution": "random",
            "random_ua": {
                "ua_system_version": ["Windows 10"]
            }
        }
    }

    def __init__(self, account):
        self.account = account

    def get_proxy(self):

        self.proxy_obj = (
            Proxy
            .select(Proxy, fn.COUNT(Profile.id).alias('profile_count'))
            .join(Profile, JOIN.LEFT_OUTER, on=(Profile.proxy == Proxy.id))
            .group_by(Proxy)
            .order_by(fn.COUNT(Profile.id).asc())
            .first()
        )

        self.proxy = {
            "proxy_soft": "other",
            "proxy_type": "socks5",
            "proxy_host": self.proxy_obj.ip,
            "proxy_port": self.proxy_obj.port,
            "proxy_user": self.proxy_obj.username,
            "proxy_password": self.proxy_obj.password,
        }
        return self

    def generate_profile_name(self):
        uid = self.account.id if self.account else str(uuid.uuid4())
        self.profile_name = f"profile_{uid}"
        return self

    def extract_cookies(self):
        import json

        storage_state = get_storage_state(self.account)
        cookies = storage_state["cookies"]
        self.cookie = json.dumps(cookies)

    def create(self):
        self.account.add_cli('Creating account ....')
        try:
            sleep(3)
            self.get_proxy()
            self.extract_cookies()
            self.generate_profile_name()
            self.payload["name"] = self.profile_name
            self.payload["group_id"] = self.folder_id
            self.payload["cookie"] = self.cookie
            self.payload["user_proxy_config"] = self.proxy

            self.send_request() \
                .create_profile_record() \
                .update_account()

        except Exception as e:
            self.account.add_cli(f"Error: {e} | {self.response_message}")
            raise Exception(f"{str(e)} | {self.response_message}")

    def send_request(self):
        url = "http://local.adspower.net:50325/api/v1/user/create"
        self.response = requests.post(url, json=self.payload, verify=False)

        try:
            json_response = self.response.json()
        except Exception:
            raise Exception(f"Invalid response: {self.response.text}")

        self.response_message = json_response.get("msg", "")
        self.response_data = json_response.get("data", {})

        return self

    def create_profile_record(self):
        self.profile = Profile.create(
            title=self.profile_name,
            folder=self.folder_id,
            profile_id=self.response_data.get('id'),
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

                added_time = last_executed_at + timedelta(seconds=TIME_TO_SLEEP)
                wait_seconds = (added_time - tehran_now()).total_seconds()

                self.account.add_cli(f'wait seconds     : {wait_seconds}')

                if wait_seconds > 0:
                    self.account.add_cli(f'We hav to wait {wait_seconds} seconds ...')
                    sleep(1)
                    continue

                getattr(self, action)()

                lock_row.last_executed_at = tehran_now()
                lock_row.save()
                break

            except OperationalError:
                print('Database is busy, waiting .5 seconds ...')
                sleep(0.5)
