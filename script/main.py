import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
import sys
from script.models.Process import Process
from script.models.Account import Account
from script.models.Lead import Lead
from script.models.Command import Command
from script.models.Spintax import Spintax
from script.models.Category import Category
from script.models.Template import Template, get_a
from script.models.Setting import Setting
from script.models.AccountHelper import get_next_account
from script.models.AccountHelper import get_next_account_for_api
from script.models.LeadSource import LeadSource, get_lead_source
from script.models.DmPost import DmPost
from script.models.DmPostLead import DmPostLead
from dotenv import load_dotenv
from script.extra.base.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserChangeBioEvent import BrowserChangeBioEvent
from script.extra.events.browser_events.BrowserChangeNameEvent import BrowserChangeNameEvent
from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.events.browser_events.BrowserPostVideoEvent import BrowserPostVideoEvent
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
from script.extra.actions.send_dm.SendDmContext import SendDmContext
from script.extra.actions.unfollow.UnfollowContext import UnfollowContext
from script.extra.actions.make_account_public.MakeAccountPublicContext import MakeAccountPublicContext
from script.extra.actions.delete_initial_posts.DeleteInitialPostsContext import DeleteInitialPostsContext
from script.extra.actions.change_name.ChangeNameContext import ChangeNameContext
from script.extra.actions.lead_generate_by_followers.LeadGenerateByFollowersContext import \
    LeadGenerateByFollowersContext
from script.extra.actions.follow.FollowContext import FollowContext
from script.extra.helper import tehran_now
from script.extra.actions.DmFollowUp import DmFollowUp
from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import LeadGenerateThroughApiContext
from script.extra.actions.lead_generate_by_page_engagement.LeadGenerateByPageEngagementContext import \
    LeadGenerateByPageEngagementContext
from script.extra.actions.lead_generate_by_post_engagement.LeadGenerateByPostEngagementContext import \
    LeadGenerateByPostEngagementContext
from script.extra.actions.login.LoginContext import LoginContext
from script.extra.helper import hours_ago
from spintax import spin
from script.models.Command import performed_command_count
from script.models.Profile import get_next
from peewee import fn
from script.extra.exceptions import CantPerformAction
from script.models.Hashtag import get_hashtag
from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import \
    LeadGenerateThroughApiContext
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy
import requests
from script.extra.events.browser_events.BrowserGetThreadMessagesEvent import BrowserGetThreadMessagesEvent
# from script.models.AdsPowerLock import AdsPowerLock
# from script.extra.modules.adspower.ProfileCreator import ProfileCreator
from datetime import timedelta, datetime
from time import sleep
from peewee import OperationalError
import pytz
# from script.extra.modules.adspower.ProfileCreator import ProfileCreator

from datetime import datetime, timedelta
from time import sleep
import pytz
from peewee import OperationalError
from script.extra.actions.DmFollowUp import DmFollowUp
from script.models.DmPost import get_dm_post_for_lead
from script.extra.exceptions import UploadedPostRecently
from script.extra.actions.send_dm_with_post.SendDmWithPostContext import SendDmWithPostContext
from script.extra.instagram.api.InstagramMobile import InstagramMobile
from script.extra.events.api_events.DmEvent import DmEvent
# def get_medias(account_instagram_id):
#     account.add_cli('Getting accounts medias')
#     account_medias = ig.user_medias(account_instagram_id, 10)
#
#     return random.choice(account_medias), account_medias
#
#
# def post_media(account, account_instagram_id):
#     account_media, account_medias = get_medias(account_instagram_id)
#
#     while account_media.media_type != 2:
#         account.add_cli(f'Account media type is {account_media.media_type} trying another one')
#         account_media = random.choice(account_medias)
#
#     if account_media.media_type == 2:
#         account.add_cli('Accounts media type is 2 trying to download the video ...')
#
#         media_path = ig.client.video_download(account_media.pk)
#         account.add_cli(f'media path {media_path}')
#
#         account.add_cli('Trying to upload the video ...')
#
#         ig.client.clip_upload(
#             media_path,
#             account_media.caption_text,
#         )
#
#     else:
#         account.add_cli('Media type is not video')
import pyotp



import logging


# تنظیمات لاگر
logging.basicConfig(
    level=logging.INFO,  # سطح لاگ: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # ذخیره در فایل
        logging.StreamHandler()          # چاپ در کنسول
    ]
)
ids =  [68,69,74, 77,83]

# while True :
# try:
account = Account.get_by_id(69)
# account = get_next_account_for_api()
# account = get_next_account()
ig = InstagramMobile(account)
ig.log_in()
sleep(2)
# bio = get_a('bio', account)
ig.media_seen('https://www.instagram.com/p/C9gw8NfMJKy/?hl=en')
    # ig.change_bio(bio.text)
    # DmEvent(account, ig).fire()
# except Exception as e:
#     print(e)



# for account_id in account_ids:
#
#     try:
#         account = Account.get_by_id(account_id)
#         ig = InstagramMobile(account)
#         ig.log_in()
#         leads = Lead.get_leads_for_dm(account, random.randint(3, 6))
#         dm_post = DmPost.select().where(DmPost.priority == 1).first()
#
#         account.add_cli('Getting accounts id')
#         # account_instagram_id = ig.get_user_id('moble.choob_zendegi')
#         # media, medias = get_medias(account_instagram_id)
#         # post_media(account, account_instagram_id)
#
#         for lead in leads:
#             account.add_cli(f'Sending direct message to {lead.username}')
#             ig.user_id_from_username(lead)
#             ig.client.direct_media_share(dm_post.media_id, [int(lead.instagram_id)])
#             text = '''
#             سلام 👋 همراه‌گرامی 🌟
# ما مشاور یکی از معتبرترین تولیدی‌های تخصصی مبلمان راحتی در کشور هستیم 🛋️
# اگه دنبال چیدمانی مدرن برای خونت هستی، ما با قیمت‌های استثنایی کنارت هستیم ✨
#
#             برای دریافت راهنمای انتخاب مدل یا ثبت سفارش، فقط کافیه بهمون پیام بدی یا با این شماره تماس بگیری:
#             📞 09129519606
#
# خوشحال میشم راهنماییت کنم 💬
#
#             https://choobozendegi.com
#             '''
#             ig.direct_send([int(lead.instagram_id)], text)
#             sleep(random.randint(1, 3))
#
#     except Exception as e:
#         print(e)

# account = get_next_account()
# browser_ig = BasePlaywright(account)
# browser_ig.init()
# LoginContext(browser_ig).fire()
# SendDmWithPostContext(browser_ig).fire()
# DeleteInitialPostsContext(browser_ig).fire()
# UnfollowContext(browser_ig).fire()
# lead = Lead.get_by_id(2950649)
# dm_post = get_or_reset_dm_post_for_lead(lead)

# print(dm_post)
# dm = DmPostLead.select().first()
# print(dm.lead_id)
# print(dm.dm_post_id)
# print(type(account.fingerprint))
# print(account.fingerprint['fingerprint_config'])

# account = Account.get_by_id(914)
# account = get_next_account()
# creator = ProfileCreator(account)
# creator.create()
# creator.delete()
# browser_ig = BasePlaywright(account)
# browser_ig.start_browser().go_to_instagram()
# BrowserDmFollowUpEvent(browser_ig).fire()
# SendDmContext(browser_ig).fire()
# BrowserGetThreadMessagesEvent(browser_ig).fire()

# UnfollowContext(browser_ig).fire()

# HowManyEventsCanHandleStrategy(account, browser_ig, None).post_action_hook()

# action, text = account.get_post_action()
#
# account.add_cli(f'We should {text}')
# action(browser_ig).fire()

# BrowserGetThreadMessagesEvent(browser_ig).fire()
# browser_ig.pause(4000000, 5000000)

# ThinkKit AI - Cathy Villalobos
# ThinkKit AI - Cathy Villalobos

# ThunkAI - Daniel Swope
# ThunkAI - Daniel Swope

# AMEUR JALLI#
# AMEUR JALLI#
# AMEUR JALLI#
# {\"result\":\"error\",\"msg\":\"Invalid channel name '#AMEUR JALLI#'\",\"code\":\"BAD_REQUEST\"}\n"
