import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin

from script.models.Setting import Setting
from script.models.Spintax import Spintax
#
from script.models.Account import Account
from script.models.Lead import Lead
from script.models.AccountHelper import *
from script.models.Message import Message
import requests
from dotenv import load_dotenv
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
from script.extra.events.browser_events.BrowserSendDmEvent import BrowserSendDmEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserMakeAccountPublic import BrowserMakeAccountPublic
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.models.Template import get_a, delete


from script.models.AccountHelper import *

lead = (Lead.select()
        .where(
    Lead.account.is_null()

).limit(1).first())


print(lead.account_id)

