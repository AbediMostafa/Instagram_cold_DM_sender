from instagrapi import Client
import json
from time import sleep
import random
from script.models.Account import Account
from script.models.Proxy import get_free_proxy

account_ids = [
    17541, 17542, 17543, 17544, 17545, 17546
]

media_ids = [
    '3922118174818128159_46861812717',
    '3922119430617775297_46861812717',
]
thread_ids = [
    340282366841710301281153566526553358884,  # TEST M1
    340282366841710301281152639546231347837,  # TEST M3
    340282366841710301281156025261400296051,  # TEST M2
    340282366841710301281152540655434306928,  # TEST M5
    340282366841710301281153227555494726152,  # TEST M4
]  # Group thread id

accounts = (
    Account
    .select()
    .where(
        (Account.service_id == 6) &
        (Account.id.in_(account_ids))
    )
)


for account in accounts:
    print(f'Trying account {account.username}')

    try:
        print(f'Setting Proxy ...')

        cl = Client()
        proxy = account.proxy
        cl.set_proxy(f"socks5://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}")

        print(f'Starting login')
        if account.mobile_session:
            settings = json.loads(account.mobile_session)
            cl.set_settings(settings)
        cl.login(account.username, account.password, verification_code=account.get_verification_code())
        account.mobile_session = json.dumps(cl.get_settings(), indent=4)
        account.save()
        print('Logged in successfully')

        for thread_id in thread_ids:
            for media_id in media_ids:
                direct_message = cl.direct_media_share(thread_ids=[int(thread_id)], media_id=media_id)
                print(f'Media {media_id} Shared in Thread {thread_id}')
                sleep(random.randint(15, 25))
        # approved = cl.direct_request_approve(thread_id=int(thread_id))
        # print(f'Approved {approved}')
            print('Making seen ...')
            thread = cl.direct_send_seen(thread_id=int(thread_id))
            print(f'Did seen {thread}')
            sleep(random.randint(15, 25))


    except Exception as e:
        print(str(e))
# print(thread)


# threads = cl.direct_threads(5)
#
# for thread in threads:
#     print(thread.pk)
#     print(thread.id)
#     print(thread.messages)
