import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Account import Account
from script.models.AccountHelper import get_next_account
from script.extra.base.BasePlaywright import BasePlaywright
from script.extra.actions.login.LoginContext import LoginContext
from script.extra.actions.connect_to_uploadPost.UploadPostConnectContext import UploadPostConnectContext
from script.extra.actions.scroll_and_like.ScrollAndLikeContext import ScrollAndLikeContext
from script.extra.actions.scroll_and_like_base_location.LocationScrollAndLikeContext import LocationScrollAndLikeContext
from script.extra.actions.location_scraper.LocationScraperContext import LocationScraperContext
from script.extra.actions.lead_generate_by_location.LeadGenerateByLocationContext import LeadGenerateByLocationContext
from script.extra.actions.follow_base_location.FollowPagesViaLocationContext import FollowPagesViaLocationContext
from script.extra.actions.generate_lead_screen_shots.LeadScreenshotContext import LeadScreenshotContext
from script.extra.actions.change_bio.ChangeBioContext import ChangeBioContext
from script.extra.actions.change_name_username.ChangeNameUsernameContext import ChangeNameUsernameContext
from script.extra.actions.make_account_public.MakeAccountPublicContext import MakeAccountPublicContext
from script.extra.actions.make_account_private.MakeAccountPrivateContext import MakeAccountPrivateContext
from script.extra.actions.order_preparer.OrderPreparerContext import OrderPreparerContext
from script.extra.api_actions.comment.ApiCommentContext import ApiCommentContext
from script.extra.api_actions.view_story.ApiViewStoryContext import ApiViewStoryContext
from script.extra.api_actions.save_post.ApiSavePostContext import ApiSavePostContext
from script.extra.api_actions.comment_and_reply.ApiCommentAndReplyContext import ApiCommentAndReplyContext
from script.extra.actions.follow.FollowContext import FollowContext
from script.models.Proxy import get_free_proxy
import requests
from  script.extra.actions.get_account_pk.GetAccountPkContext import GetAccountPkContext
# account = get_next_account(service_id=6)
account = Account.get_by_id(4133)

browser_ig = BasePlaywright(account)
browser_ig.init()
LoginContext(browser_ig).fire()
# ScrollAndLikeContext(browser_ig).fire()
FollowContext(browser_ig).fire()

if browser_ig:
    browser_ig.cleanup()

# LocationScraperContext(browser_ig).fire()
# LocationScrollAndLikeContext(browser_ig).fire()
# LeadGenerateByLocationContext(browser_ig).fire()
# FollowPagesViaLocationContext(browser_ig).fire()
# UploadPostConnectContext(browser_ig).fire()
# ScrollAndLikeContext(browser_ig).fire()
# ChangeBioContext(browser_ig).fire()
# ChangeNameUsernameContext(browser_ig).fire()
# MakeAccountPrivateContext(browser_ig).fire()
# OrderPreparerContext(browser_ig).fire()
# ApiCommentAndReplyContext(browser_ig).fire()
# ApiCommentContext(browser_ig).fire()
# ApiViewStoryContext(browser_ig).fire()
# ApiSavePostContext(browser_ig).fire()
# LeadScreenshotContext(browser_ig).fire()