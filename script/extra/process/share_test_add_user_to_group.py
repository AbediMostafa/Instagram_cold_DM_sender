from instagrapi import Client
import json
from time import sleep
import random
from pathlib import Path

from script.models.Account import Account

PROGRESS_FILE = "thread_add_progress.json"

thread_ids = [
    340282366841710301281153722478534468467,
    340282366841710301281179031378682334110,
    340282366841710301281152686006109809287,
    340282366841710301281152684458363313619,
]

def load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=4)


def progress_key(user_id, thread_id):
    return f"{user_id}:{thread_id}"


progress = load_progress()

accounts = (
    Account
    .select()
    .where(Account.service_id == 6)
)

# 3865
# 4203
sender_account = Account.get_by_id(4327)

cl = Client()
proxy = sender_account.proxy
cl.set_proxy(f"socks5://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}")

if sender_account.mobile_session:
    cl.set_settings(json.loads(sender_account.mobile_session))

cl.login(
    sender_account.username,
    sender_account.password,
    verification_code=sender_account.get_verification_code()
)

sender_account.mobile_session = json.dumps(cl.get_settings(), indent=4)
sender_account.save()

user_ids = [account.instagram_id for account in accounts]
user_ids = user_ids[::-1]

# for thread_id in thread_ids:
#     approved = cl.direct_request_approve(thread_id=int(thread_id))
#     print(f'Approved {approved}')

for user_id in user_ids:

    for thread_id in thread_ids:

        key = progress_key(user_id, thread_id)

        # Skip anything already processed
        if key in progress:
            print(
                f"Skipping user={user_id} thread={thread_id} "
                f"status={progress[key]['status']}"
            )
            continue

        try:
            cl.direct_thread_add_users(
                thread_id=int(thread_id),
                user_ids=[int(user_id)]
            )

            progress[key] = {
                "status": "success"
            }

            save_progress(progress)

            print(
                f"SUCCESS user={user_id} -> thread={thread_id}"
            )

            sleep(random.randint(3, 5))

        except Exception as e:
            progress[key] = {
                "status": "error",
                "error": str(e)
            }

            save_progress(progress)

            print(
                f"ERROR user={user_id} -> thread={thread_id}: {e}"
            )

            sleep(random.randint(3, 5))