import sys
import os
from peewee import fn, SQL

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Command import Command
from script.models.Lead import Lead
from script.models.Account import Account
from datetime import datetime, timedelta
from tzlocal import get_localzone
from script.models.Account import Account
from script.models.Warning import Warning
from script.extra.hooks.CheckForWarningsHook import CheckForWarningsHook
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.extra.hooks.RecordLastActivityHook import RecordLastActivityHook
from script.extra.hooks.CheckForLastLoginHook import CheckForLastLoginHook
from script.extra.instagram.InstagramMobile import InstagramMobile
import random
from time import sleep

account = Account.get_by_id(585)
account_as_lead = Account.get_by_id(1)

ig = InstagramMobile(account)
ig.log_in()
counter = 0

instagram_id = ig.user_id_from_username(account_as_lead)
print(f'Accounts ID: {instagram_id}')

while True:
    counter += 1
    print(f'Sending direct for the {counter} time ...')
    ig.direct_send([instagram_id], f'Hi {counter}')
    print('Sent direct successfully')
    sleep(random.randint(1, 5))
