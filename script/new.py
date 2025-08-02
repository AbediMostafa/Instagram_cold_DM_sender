import sys
import os
sys.path.append(r"C:\Users\admin\AppData\Roaming\Python\Python312\site-packages")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.AccountHelper import *
from script.extra.base.BasePlaywright import BasePlaywright
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
from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import LeadGenerateThroughApiContext
from script.models.Lead import Lead
from datetime import datetime, timedelta
from spintax import spin
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from script.extra.modules.bulkacc.TmpMail import TmpMail
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
import pytz
from script.extra.hooks.RecordLastActivityHook import RecordLastActivityHook
from script.extra.actions.Follow import Follow
from script.models.Command import Command
from script.models.Hashtag import Hashtag, get_hashtag
from script.extra.parsers.GridPostParser import GridPostParser
from script.extra.actions.send_dm.SendDmContext import SendDmContext
from script.extra.actions.follow_good_pages.FollowGoodPagesContext import FollowGoodPagesContext
#
from script.models.Process import Process
from spintax import spin
import traceback
from script.extra.actions.login.LoginContext import LoginContext



if len(sys.argv) < 2:
    print("Usage: python new.py <account_id>")
    sys.exit(1)

account_id = sys.argv[1]
account = Account.get_by_id(account_id)
if not account:
    sys.exit(1)
try:
    browser_ig = BasePlaywright(account)
    browser_ig.init()
    LoginContext(browser_ig).fire()
    FollowGoodPagesContext(browser_ig).fire()


except Exception as e:
    print(str(e))
    print(traceback.format_exc())
    pass


# CheckForAccountActionsHook(account)
#
# browser_ig = BasePlaywright(account)
# browser_ig.start_browser().go_to_instagram()
# SendDmContext(browser_ig).fire()
# BrowserLoginEvent(browser_ig).fire()
# browser_ig.pause(4000000, 5000000)
#
# for i in range(50):
#     path = 'C:\\Users\\Administrator\\Desktop\\project\\backend\\storage\\app\\public\\uploads\\avatar\\10\\11\\uqXjpNaY1P7Wt67Qc3ors5s2dlyTfjWe9MvpuxPR.jpg'
#     folder = 'C:\\Users\\Administrator\\Desktop\\project\\backend\\storage\\app\\public\\uploads\\avatar\\10\\11'
#     process_image(path, folder)
#
# cli = Cli.get_by_id(46721676)
# print(cli.created_at)
# account = Account.get_by_id(2334)
# CheckForAccountActionsHook(account)
# browser_ig = BasePlaywright(account)
# browser_ig.start_browser().go_to_instagram()
# BrowserSendDmEvent(browser_ig).fire()
# # BrowserLoginEvent(browser_ig).fire()

# RecordLastActivityHook(account)
# account.create_command('dm follow up', 'processing')
#
# print(account.number_of_custom_message_commands)
#
# for command in account.custom_message_commands:
#     print(command.id)
#
# # BrowserChangeUsernameEvent(browser_ig).fire()
# #
