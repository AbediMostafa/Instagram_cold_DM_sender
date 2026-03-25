import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from script.models.Account import Account
# from script.models.Lead import Lead

import pandas as pd
import csv
import sys

import random

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
from script.extra.actions.get_lead_pk.GetLeadPkContext import GetLeadPkContext
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
from script.extra.actions.get_contact_information.GetContactInformationContext import GetContactInformationContext
from script.models.Warning import Warning

from script.extra.helper import hours_ago
from spintax import spin
from script.models.Command import performed_command_count
from script.models.Profile import get_next
from peewee import fn
from script.extra.exceptions import CantPerformAction
from script.models.Hashtag import get_hashtag
from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import \
    LeadGenerateThroughApiContext
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
from script.models.Proxy import get_free_proxy
from script.extra.exceptions import UploadedPostRecently
from script.extra.actions.send_dm_with_post.SendDmWithPostContext import SendDmWithPostContext
from script.extra.actions.check_system_username_with_ig_username.CheckSystemUsernameWithIgUsernameContext import \
    CheckSystemUsernameWithIgUsernameContext
from script.extra.actions.get_profile_screen_shot.GetProfileScreenShotContext import GetProfileScreenShotContext
from script.extra.actions.activated_2fa_code.Activate2faCodeContext import Activate2faCodeContext
from script.extra.actions.lead_generate_following_other_leads.LeadGenerateByInstagramSuggestionContext import \
    LeadGenerateByInstagramSuggestionContext
from script.extra.instagram.api.InstagramMobile import InstagramMobile
from peewee import *
from script.models.Proxy import get_free_proxy
from script.models.Proxy import Proxy
from script.extra.actions.lead_generate_by_linkedin.LeadGenerateByLinkedinContext import LeadGenerateByLinkedinContext
# from script.extra.actions.comment.BrowserCommentEvent import get_free_comment
import requests
from script.models.EnrichedLead import EnrichedLead, get_free_enriched_lead
from script.models.EnrichedLead import EnrichedLead, get_free_enriched_lead
# from script.models.Order import get_next_order_for_account
from script.models.OrderComment import get_next_comment_for_order, OrderComment
from script.extra.actions.register_email.RegisterEmailContext import RegisterEmailContext
from script.extra.actions.post_image_from_folder.PostImageFromFolderContext import PostImageFromFolderContext
from script.extra.actions.post_from_folder_and_comment.PostFromFolderAndCommentContext import \
    PostFromFolderAndCommentContext
from script.extra.actions.comment_on_others_post.CommentOnOthersPostContext import CommentOnOthersPostContext
# from script.extra.actions.like_and_comment.LikeAndCommentContext import LikeAndCommentContext
# from script.extra.actions.view_story.ViewStoryContext import ViewStoryContext
# from script.extra.actions.save_post.SavePostContext import SavePostContext


from script.extra.actions.order_preparer.OrderPreparerContext import OrderPreparerContext
from script.extra.api_actions.view_story.ApiViewStoryContext import ApiViewStoryContext
from script.extra.api_actions.save_post.ApiSavePostContext import ApiSavePostContext
from script.extra.api_actions.comment.ApiCommentContext import ApiCommentContext

from urllib.parse import urlparse
from script.extra.actions.change_name_username.ChangeNameUsernameContext import ChangeNameUsernameContext
from script.extra.routes import *
# from script.extra.actions.like_and_comment.LikeAndCommentContext import LikeAndCommentContext
from script.extra.actions.lead_profile_extractor.LeadProfileExtractor import LeadProfileExtractor
from script.extra.actions.reels_average_extractor.ReelsAverageExtractor import ReelsAverageExtractor
from script.ProcessManager import ProcessManager
from script.models.Workflow import Workflow
from script.models.Order import Order
from script.models.Module import Module
from script.models.Service import Service
from script.models.Balance import Balance
from script.models.Profile import Profile
from script.extra.actions.scroll_and_like.ScrollAndLikeContext import ScrollAndLikeContext
from script.extra.actions.change_bio.ChangeBioContext import ChangeBioContext
from script.extra.actions.make_account_private.MakeAccountPrivateContext import MakeAccountPrivateContext
from script.extra.routes import *
from script.models.AccountHelper import get_storage_state
from script.extra.api_actions.BrowserApiViewStoryEvent import BrowserApiViewStoryEvent
from datetime import timedelta
from script.extra.helper import tehran_now
# from script.models.Order import get_next_order_for_account
import json

import requests
import requests
import uuid
import json
import requests
from script.models.Profile import Profile
from script.models.Proxy import get_free_proxy

url = "https://api.adspower.com/fbcc/user/single-import-user"

headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded",
    "cpl": "feaae21d9508e8a0b41fd3f91af0442b008662c38d6b2e51",
    "origin": "https://app.adspower.com",
    "referer": "https://app.adspower.com/",
    "user-agent": "Mozilla/5.0"
}

cookies = {
    "__SYS_ID": "98607baca5b939a5a63e764b830814ff",
    "LOCAL_KEY_IN_WEBSITE": "feaae21d9508e8a0b41fd3f91af0442b008662c38d6b2e51",
}

# base fingerprint config (reuse)
fingerprint_config = {
    "client_hints": {
        "bitness": "64",
        "platform": "Windows",
        "architecture": "x86",
        "ua_full_version": "143.0.7499.146",
        "platform_version": "15.0.0"
    },
    "fonts": "all",
    "canvas": "0",
    "webgl": "2",
    "audio": "1",
    "webrtc": "disabled",
    "browser": "chrome",
    "language": ["en-US","en"],
    "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.146 Safari/537.36",
}

for i in range(200):
    sleep(3)
    try:
        # ✅ generate uuid name
        profile_name = f"profile_{uuid.uuid4().hex[:12]}"

        data = {
            "name": profile_name,
            "batch_id": 0,
            "switch_random_finger": 1,
            "browser_run_args": "",
            "proxytype": "noproxy",
            "proxy": "",
            "fingerprint_config": json.dumps(fingerprint_config)
        }

        response = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            data=data
        )

        print(f"{i + 1}/200 -> {response.status_code}")
        print(f"{i + 1}/200 -> {response.json()}")

        if response.status_code == 200:
            res_json = response.json()

            # ⚠️ adjust this based on actual API response
            profile_id = str(res_json.get("data", {}).get("id", ""))
            print(profile_id)

            # ✅ save to DB
            profile = Profile.create(
                title=profile_name,
                profile_id=profile_id,
                folder="default",
            )
            print(profile)

        else:
            print(response.text)

    except Exception as e:
        print(f"Error at {i}: {e}")

data = "name=salamsalam&batch_id=0&switch_random_finger=1&browser_run_args=&proxytype=noproxy&proxy=&fingerprint_config=%7B%22client_hints%22%3A%7B%22model%22%3A%22%22%2C%22wow64%22%3A%22%22%2C%22mobile%22%3A%22%22%2C%22bitness%22%3A%2264%22%2C%22platform%22%3A%22Windows%22%2C%22architecture%22%3A%22x86%22%2C%22ua_full_version%22%3A%22143.0.7499.146%22%2C%22platform_version%22%3A%2215.0.0%22%7D%2C%22fonts%22%3A%22all%22%2C%22canvas%22%3A%220%22%2C%22webgl%22%3A%222%22%2C%22audio%22%3A%221%22%2C%22webrtc%22%3A%22disabled%22%2C%22gpu%22%3A%220%22%2C%22tls%22%3A%22%22%2C%22page_language%22%3A%22native%22%2C%22allow_scan_ports%22%3A%22%22%2C%22screen_resolution%22%3A%22none%22%2C%22automatic_timezone%22%3A%221%22%2C%22media_devices%22%3A%221%22%2C%22client_rects%22%3A%221%22%2C%22webgl_config%22%3A%7B%22unmasked_vendor%22%3A%22Google%20Inc.%20(NVIDIA)%22%2C%22unmasked_renderer%22%3A%22ANGLE%20(NVIDIA%2C%20NVIDIA%20GeForce%20GTX%20650%20(0x00002504)%20Direct3D11%20vs_5_0%20ps_5_0%2C%20D3D11-27.21.14.6589)%22%2C%22system%22%3A%22Windows%22%2C%22webgpu%22%3A%7B%22webgpu_switch%22%3A%221%22%7D%7D%2C%22webgl_image%22%3A%220%22%2C%22do_not_track%22%3A%22default%22%2C%22hardware_concurrency%22%3A%2210%22%2C%22device_memory%22%3A%228%22%2C%22tls_switch%22%3A%220%22%2C%22scan_port_type%22%3A%221%22%2C%22device_name_switch%22%3A%222%22%2C%22device_name%22%3A%22PC-3PA6TET%22%2C%22speech_switch%22%3A%221%22%2C%22audio_id%22%3A%22-588%22%2C%22client_rects_id%22%3A%224139%22%2C%22dpr%22%3A2%2C%22flash%22%3A%22block%22%2C%22location%22%3A%22ask%22%2C%22accuracy%22%3A1000%2C%22browser%22%3A%22chrome%22%2C%22location_switch%22%3A%221%22%2C%22language_switch%22%3A%221%22%2C%22page_language_switch%22%3A%221%22%2C%22language%22%3A%22en-US%2Cen%22%2C%22ua%22%3A%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F143.0.7499.146%20Safari%2F537.36%22%2C%22browser_kernel_config%22%3A%7B%22version%22%3A%22ua_auto%22%2C%22type%22%3A%22chrome%22%7D%2C%22sys_resolution%22%3A%22%22%2C%22sys_dpr%22%3A%22%22%2C%22mac_address_config%22%3A%7B%22model%22%3A%222%22%2C%22address%22%3A%2210-7B-44-A9-87-98%22%7D%7D"
