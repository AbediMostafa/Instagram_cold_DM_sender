import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from script.models.Account import Account
# from script.models.Lead import Lead

import pandas as pd
import csv
import sys

count = 0
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
# from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
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
# from script.extra.actions.connect_to_uploadPost.UploadPostConnectContext import UploadPostConnectContext


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
from datetime import timedelta
from script.extra.helper import tehran_now
# from script.models.Order import get_next_order_for_account
import json
from script.extra.actions.lead_full_data_extractor.LeadFullDataExtractor import LeadFullDataExtractor
from script.extra.actions.post_media.PostMediaContext import PostMediaContext
# account = Account.get_by_id(15)
# lead = Lead.select_lead_for_profile(account)
# print(lead)
# template = Lead.get_a_template(account, 'bio')
#
# print(template)

# oc = OrderComment.get_by_id(210874)
# oc.updated_at = tehran_now()
# oc.save()
from script.models.OrderComment import release_stuck_comments

# print(updated_counts.count())
# account = get_next_account()
account = Account.get_by_id(151)
# # order = get_next_order_for_account(account)
# # print(order)
browser_ig = BasePlaywright(account)
browser_ig.init()
LoginContext(browser_ig).fire()
PostMediaContext(browser_ig).fire()
# OrderPreparerContext(browser_ig).fire()
# ApiCommentContext(browser_ig).fire()
# ApiSavePostContext(browser_ig).fire()
# StoryPreparerContext(browser_ig).fire()
# ApiViewStoryContext(browser_ig).fire()
# ViewStoryContext(browser_ig).fire()
# ViewAllStoriesContext(browser_ig).fire()
# SavePostContext(browser_ig).fire()
# LikeAndCommentContext(browser_ig).fire()
# LeadGenerateByPostEngagementContext(browser_ig).fire()
# ChangeNameUsernameContext(browser_ig).fire()
# CommentOnOthersPostContext(browser_ig).fire()
# ReelsAverageExtractor(browser_ig).fire()
# PostImageFromFolderContext(browser_ig).fire()
# LikeAndCommentContext(browser_ig).fire()
# MakeAccountPublicContext(browser_ig).fire()
# Format A: /p/{code}
# BrowserChangeBioEvent(browser_ig).fire()
# GetContactInformationContext(browser_ig).fire()
# response = requests.get(url, verify=False)
# print(response.json().get('data').get('status'))
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
