import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# from script.models.Account import Account
# from script.models.Command import Command
from script.models.AccountTemplate import AccountTemplate
from script.models.Template import Template
# from datetime import datetime, timedelta
# from script.extra.process.Process import Process
from script.models.AccountHelper import *
from time import sleep
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin

from script.extra.instagram.api.InstagramMobile import InstagramMobile
# from script.extra.events.api_events.GetThreadMessagesEvent import GetThreadMessagesEvent
from script.extra.events.api_events.PostVideoEvent import PostVideoEvent
from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
from script.extra.events.browser_events.BrowserChangeNameEvent import BrowserChangeNameEvent
from script.extra.events.browser_events.BrowserChangeBioEvent import BrowserChangeBioEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserLoomFollowUpEvent import BrowserLoomFollowUpEvent
from script.extra.events.browser_events.BrowserDeleteInitialPostsEvent import BrowserDeleteInitialPostsEvent
from script.extra.events.browser_events.BrowserGetThreadMessagesEvent import BrowserGetThreadMessagesEvent
from script.extra.events.browser_events.BrowserSendDmEvent import BrowserSendDmEvent
# from script.extra.events.browser_events.BrowserPostVideoEvent import BrowserPostVideoEvent
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
# from script.extra.events.api_events.ChangeAvatarEvent import ChangeAvatarEvent
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
from script.extra.events.browser_events.BrowserGoToTargetAccountAndExplorePosts import \
    BrowserGoToTargetAccountAndExplorePosts
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.hooks.CheckForAccountActionsHook import CheckForAccountActionsHook

from script.models.Lead import Lead
from script.models.Thread import Thread
from script.models.Message import Message
from script.models.Command import Command
from script.extra.actions.DM import DM

account = Account.get_by_id(1816)
# account = get_next_account()
CheckForAccountActionsHook(account)
browser_ig = BasePlaywright(account)
BrowserChangeAvatarEvent(browser_ig).fire()
browser_ig.pause(1000000, 2000000)
