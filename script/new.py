import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import requests
import time
from playwright.sync_api import sync_playwright
import json
from script.models.Account import Account
from script.models.Color import Color
import time

from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent

from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin
from script.extra.helper import *
from script.models.Setting import Setting
from script.models.Spintax import Spintax
#
from script.models.Account import Account
from script.models.Lead import Lead
from script.models.Profile import Profile
from script.models.AccountHelper import *
from script.models.Message import Message
from script.models.Tag import Tag
from script.models.Taggable import Taggable
import requests
from dotenv import load_dotenv
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
from script.extra.events.browser_events.BrowserSendDmEvent import BrowserSendDmEvent
from script.extra.events.browser_events.BrowserGetThreadMessagesEvent import BrowserGetThreadMessagesEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserMakeAccountPublic import BrowserMakeAccountPublic
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserChangeNameEvent import BrowserChangeNameEvent
from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
from script.models.Template import get_a, delete
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.extra.hooks.CheckForAccountActionsHook import CheckForAccountActionsHook
from script.models.Lead import Lead
from datetime import datetime, timedelta
from spintax import spin
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from script.extra.modules.bulkacc.TmpMail import TmpMail
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent

# accountId = 1151
# account = Account.get_by_id(accountId)
# CheckForAccountActionsHook(account)
# browser_ig = BasePlaywright(account)
# browser_ig.start_browser().go_to_instagram()
# BrowserSendDmEvent(browser_ig).fire()
# BrowserLoginEvent(browser_ig).fire()
# browser_ig.pause(4000000, 5000000)
#
# for i in range(50):
#     path = 'C:\\Users\\Administrator\\Desktop\\project\\backend\\storage\\app\\public\\uploads\\avatar\\10\\11\\uqXjpNaY1P7Wt67Qc3ors5s2dlyTfjWe9MvpuxPR.jpg'
#     folder = 'C:\\Users\\Administrator\\Desktop\\project\\backend\\storage\\app\\public\\uploads\\avatar\\10\\11'
#     process_image(path, folder)

#
account = Account.get_by_id(2877)

CheckForAccountActionsHook(account)
# browser_ig = BasePlaywright(account)
# browser_ig.start_browser().go_to_instagram()
# # BrowserLoginEvent(browser_ig).fire()
#
# print(account.number_of_custom_message_commands)
#
# for command in account.custom_message_commands:
#     print(command.id)
#
# # BrowserChangeUsernameEvent(browser_ig).fire()
# #

