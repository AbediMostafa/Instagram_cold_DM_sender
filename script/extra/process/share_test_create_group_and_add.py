from instagrapi import Client
import json
from time import sleep
import random
from script.models.Account import Account

accounts = (
    Account
    .select()
    .where(
        (Account.service_id == 6)
    )
)

account = Account.get_by_id(4327)
print(account.id)
print(account.username)

account_ids = [account.instagram_id for account in accounts]

# USERNAME = 'ommar.reyes'
# PASSWORD = 'reyes80537'
# TWOFACTOR = 'J3HO2NJEKS2PCFPBAKURXLRD4EHBQYT7'
media_id = '3917314774771201192'
thread_ids = [
    340282366841710301281153722478534468467,
    340282366841710301281179031378682334110,
    340282366841710301281152686006109809287,
    340282366841710301281152684458363313619,
]

cl = Client()
if account.mobile_session:
    settings = json.loads(account.mobile_session)
    cl.set_settings(settings)
cl.login(account.username, account.password, verification_code=account.get_verification_code())
account.mobile_session = json.dumps(cl.get_settings(), indent=4)
account.save()

initial_users = account_ids[:2]
print(f'selected initial users : {initial_users}')
print(f'Created thread {thread_id}')

for _ in range(2):
    thread_id = cl.direct_thread_create(user_ids=initial_users, title=f'TEST_SHARE_{_}')
    print(f'Created thread {thread_id}')
    sleep(random.randint(3, 5))

exit()
'''
Created thread 340282366841710301281153722478534468467
Created thread 340282366841710301281179031378682334110
Created thread 340282366841710301281152686006109809287
Created thread 340282366841710301281152684458363313619
'''
remaining_users = account_ids[::-1]

for i in range(0, len(remaining_users), 1):
    batch = remaining_users[i:i + 1]

    try:
        cl.direct_thread_add_users(
            thread_id=int(thread_id),
            user_ids=batch
        )

        print(f"Added batch: {batch}")

        sleep(random.randint(3, 5))

    except Exception as e:
        print(f"Failed adding batch {batch}: {e}")
