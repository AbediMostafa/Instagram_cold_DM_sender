import sys
import os
import time
import math
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin
from script.extra.helper import *
from script.models.Setting import Setting
from script.models.Spintax import Spintax
#
from script.models.Account import Account
from script.models.Thread import Thread
from script.models.Lead import Lead
from script.models.AccountHelper import *
from script.models.Message import Message
import requests
from dotenv import load_dotenv
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
# from script.extra.events.browser_events.BrowserSendDmEvent import BrowserSendDmEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserLoomFollowUpEvent import BrowserLoomFollowUpEvent
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserSeeStories import BrowserSeeStories
from script.extra.events.browser_events.BrowserMakeAccountPublic import BrowserMakeAccountPublic
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserDeleteInitialPostsEvent import BrowserDeleteInitialPostsEvent
from script.extra.events.browser_events.BrowserPostVideoEvent import BrowserPostVideoEvent
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent

from script.models.Template import get_a, delete
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.extra.hooks.CheckForAccountActionsHook import CheckForAccountActionsHook
from script.extra.hooks.RecordLastActivityHook import RecordLastActivityHook
from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent

from script.models.Lead import Lead
from datetime import datetime, timedelta
from spintax import spin
import random
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware

from script.models.AccountHelper import *
from script.models.ScreenResolution import get_next_screen_resolution
from script.models.AccountHelper import get_next_account

load_dotenv()


def display_menu():
    print("\n==================== MENU ====================")
    print("1. Change Proxy to Residential")
    print("2. Delete Account")
    print("3. Do Nothing")
    print("4. Post Carousel")
    print("5. Post Image")
    print("6. Post Video")
    print("=============================================")


def start_browser(browser_ig):
    browser_ig.start_browser().go_to_instagram()
    BrowserLoginEvent(browser_ig).fire()


def after_login(account, browser_ig):
    display_menu()
    user_input = input("Your choice: ").strip()

    if user_input == '1':
        browser_ig.cleanup()
        sleep(3)

        proxy = account.update_proxy_to_residential()
        account.add_cli(f"Proxy updated to residential: {proxy}")
        sleep(3)
        browser_ig = BasePlaywright(account)
        start_browser(browser_ig)
        another_user_input = input("Update to custom? ").strip()

        if another_user_input == '1':
            sleep(3)
            browser_ig.cleanup()
            proxy = account.update_proxy_to_custom()
            sleep(3)

            browser_ig = BasePlaywright(account)
            start_browser(browser_ig)

    elif user_input == '2':
        confirm = input("Are you sure you want to delete the account? (yes/no): ").strip().lower()
        if confirm == 'yes':
            account.delete_instance()  # Assuming a delete method exists for accounts
            print("Account deleted successfully.")

    elif user_input == '3':
        browser_ig.cleanup()
        return True

    elif user_input == '4':
        BrowserPostCarouselEvent(browser_ig).fire()

    elif user_input == '5':
        BrowserPostImageEvent(browser_ig).fire()

    elif user_input == '6':
        BrowserPostVideoEvent(browser_ig).fire()

    browser_ig.cleanup()

def color_answer():
    print("\n==================== select color ====================")
    print("1. orange")
    print("2. yellow")
    print("3. green")
    print("4. blue")
    print("5. purple")
    print("6. aquamarine")
    print("7. red")
    print("=============================================")
    pass

while True:
    try:
        account = get_next_account()
        CheckForAccountActionsHook(account)
        account.add_cli(f'tags .................... {account.tags(False)}')
        account.add_cli(f'number of posts ......... {account.get_number_of_successful_posts()}')
        account.add_cli(f'latest command time  .... {account.get_latest_successful_command_time()}')
        account.add_cli(f'username changed  ....... {account.username_changed}')
        account.add_cli(f'name changed  ........... {account.has('name')}')
        account.add_cli(f'bio changed  ............ {account.has('bio')}')
        account.add_cli(f'avatar changed  ......... {account.avatar_changed}')
        account.add_cli(f'exact proxy  ............ {account.get_exact_proxy()}')

        browser_ig = BasePlaywright(account)
        try:
            start_browser(browser_ig)
            after_login(account, browser_ig)
        except Exception as e:
            print(str(e))
            after_login(account, browser_ig)



    except Exception as e:
        print(str(e))
        after_login(account, browser_ig)


