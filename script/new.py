import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import requests
import time
from playwright.sync_api import sync_playwright
import json
from script.models.Account import Account

MLX_BASE = "https://api.multilogin.com"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

USERNAME = "mostafaaabedi@gmail.com"
PASSWORD = "Mosthegreate123@#$"

PROFILE_ID = "0fc2edc7-ff80-4625-b3e8-b62758d53932"
FOLDER_ID = "mass_dm"


def sign_in() -> str:
    payload = {
        "email": USERNAME,
        "password": hashlib.md5(PASSWORD.encode()).hexdigest(),
    }
    r = requests.post(f"{MLX_BASE}/user/signin", json=payload)
    if r.status_code != 200:
        print(f"\nError during login: {r.text}\n")
    else:
        response = r.json()["data"]
        token = response["token"]

        return token


HEADERS["Authorization"] = f"Bearer {sign_in()}"


def start_profile():
    with sync_playwright() as pw:
        resp = requests.get(
            f"https://launcher.mlx.yt:45001/api/v2/profile/f/{FOLDER_ID}/p/{PROFILE_ID}/start?automation_type=playwright&headless_mode=false",
            headers=HEADERS)
        resp_json = resp.json()

        if resp.status_code != 200:
            print(f"\nError while starting profile: {resp.text}\n")
            return
        else:
            print(f"\nProfile {PROFILE_ID} started.\n")
            browserPort = resp_json["data"]["port"]
            print(browserPort)
            browserURL = f"http://127.0.0.1:{browserPort}"
            browser = pw.chromium.connect_over_cdp(endpoint_url=browserURL)
            account = Account.get_by_id(311)
            context = browser.new_context(
                proxy={
                    "server": f"http://{account.proxy.ip}:{account.proxy.port}",
                    "username": account.proxy.username,
                    "password": account.proxy.password
                },
                storage_state=account.get_session()
            )
            page = context.new_page()
            page.goto('https://www.instagram.com')
            page.wait_for_timeout(1000000)
            time.sleep(5)
            page.screenshot(path='example.png')
            page.close()


start_profile()
