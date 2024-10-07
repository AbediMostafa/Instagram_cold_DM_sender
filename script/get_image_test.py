import requests
from script.models.Color import get_next_color
from script.models.Account import Account
from script.models.AccountHelper import get_next_account
from script.models.AccountTemplate import AccountTemplate
from script.models.Template import Template
from dotenv import load_dotenv
import os
import tempfile
from script.extra.helper import *

account  = Account.get_by_id(564)
carousel = account.get_a_carousel()

for ca in carousel:
    ca.salam = 'salam'
    print(ca.uid)

print(carousel[0].salam)