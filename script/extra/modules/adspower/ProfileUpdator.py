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
    folder_id = "5780347"
    response = "5780347"
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

    def send_request(self):
        url = "http://local.adspower.net:50325/api/v1/user/create"
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
