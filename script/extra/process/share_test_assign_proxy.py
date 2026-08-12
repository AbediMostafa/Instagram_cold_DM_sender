from instagrapi import Client
import json
from time import sleep
import random
from script.models.Account import Account
from script.models.Proxy import get_free_proxy

accounts = (
    Account
    .select()
    .where(
        (Account.service_id == 6)
    )
)



for account in accounts:
    print(account.proxy_id)
    # proxy = get_free_proxy()
    # account.proxy = proxy
    # account.save()

