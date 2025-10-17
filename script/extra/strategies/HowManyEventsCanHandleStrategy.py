import random

from script.extra.events.browser_events.BrowserScrollAndLikeEvent import BrowserScrollAndLikeEvent
from script.extra.events.browser_events.BrowserDeleteInitialPostsEvent import BrowserDeleteInitialPostsEvent
from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserLoomFollowUpEvent import BrowserLoomFollowUpEvent
from script.extra.events.browser_events.BrowserChangeBioEvent import BrowserChangeBioEvent
from script.extra.events.browser_events.BrowserChangeNameEvent import BrowserChangeNameEvent
from script.extra.events.browser_events.BrowserGetThreadMessagesEvent import BrowserGetThreadMessagesEvent
from script.extra.events.browser_events.BrowserSendCustomMessage import BrowserSendCustomMessage
from script.extra.actions.get_lead_pk.GetLeadPkContext import GetLeadPkContext
from script.extra.actions.get_profile_screen_shot.GetProfileScreenShotContext import GetProfileScreenShotContext
from script.extra.actions.get_contact_information.GetContactInformationContext import GetContactInformationContext
from script.extra.actions.register_email.RegisterEmailContext import RegisterEmailContext
from script.extra.actions.activated_2fa_code.Activate2faCodeContext import Activate2faCodeContext


from script.extra.events.browser_events.BrowserMakeAccountPublic import BrowserMakeAccountPublic
from script.extra.events.browser_events.BrowserSeeStories import BrowserSeeStories
from script.extra.actions.follow.FollowContext import FollowContext

from script.extra.events.browser_events.BrowserGoToTargetAccountAndExplorePosts import \
    BrowserGoToTargetAccountAndExplorePosts

from script.extra.actions.send_dm.SendDmContext import SendDmContext
from script.extra.actions.send_dm_with_post.SendDmWithPostContext import SendDmWithPostContext
from script.extra.actions.make_account_public.MakeAccountPublicContext import MakeAccountPublicContext
from script.extra.actions.delete_initial_posts.DeleteInitialPostsContext import DeleteInitialPostsContext
from script.extra.actions.change_name.ChangeNameContext import ChangeNameContext
from script.extra.actions.follow_good_pages.FollowGoodPagesContext import FollowGoodPagesContext
from script.extra.actions.unfollow.UnfollowContext import UnfollowContext

from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import LeadGenerateThroughApiContext
from script.extra.actions.lead_generate_by_followers.LeadGenerateByFollowersContext import \
    LeadGenerateByFollowersContext

from script.extra.actions.lead_generate_by_page_engagement.LeadGenerateByPageEngagementContext import \
    LeadGenerateByPageEngagementContext

from script.extra.actions.lead_generate_by_post_engagement.LeadGenerateByPostEngagementContext import \
    LeadGenerateByPostEngagementContext

from script.extra.actions.check_system_username_with_ig_username.CheckSystemUsernameWithIgUsernameContext import CheckSystemUsernameWithIgUsernameContext



class HowManyEventsCanHandleStrategy:
    events = None
    passed_days = None
    browser_ig = None
    api_ig = None
    account = None

    def __init__(self, account, browser_ig, api_ig):
        self.account = account
        self.browser_ig = browser_ig
        self.api_ig = api_ig

    def run(self):

        # self.pre_action_hook()
        self.run_actions()
        # self.post_action_hook()

    def pre_action_hook(self):
        BrowserSendCustomMessage(self.browser_ig).fire()
        BrowserGetThreadMessagesEvent(self.browser_ig).fire()

    def post_action_hook(self):
        from script.extra.exceptions import UploadedPostRecently

        if self.account.initial_posts_deleted:
            self.account.add_cli('We can post now')

            try:
                # Get type of post and it's text
                action, text = self.account.get_post_action()

                self.account.add_cli(f'We should {text}')
                action(self.browser_ig).fire()

            except UploadedPostRecently as e:
                self.account.add_cli(str(e))

    def select_random_explore_action(self):
        # Define a list of random actions to choose from each day
        random_actions = [
            BrowserScrollAndLikeEvent,
            BrowserGotoExploreEvent,
            BrowserSeeStories,
            # BrowserGoToTargetAccountAndExplorePosts(self.browser_ig, user_type='lead',
            #                                         user_numbers=random.randint(1, 4),
            #                                         post_numbers=random.randint(1, 4),
            #                                         load_more_comments_number=5, scroll_before_click=True,
            #                                         number_of_scrolls=random.randint(6, 10)),
            # BrowserGoToTargetAccountAndExplorePosts(self.browser_ig, user_type='account',
            #                                         user_numbers=random.randint(1, 3),
            #                                         post_numbers=random.randint(1, 5),
            #                                         load_more_comments_number=5, scroll_before_click=True,
            #                                         number_of_scrolls=random.randint(2, 7)),
            # BrowserGoToTargetAccountAndExplorePosts(self.browser_ig, user_type='random_user',
            #                                         user_numbers=random.randint(1, 3),
            #                                         post_numbers=random.randint(1, 5),
            #                                         load_more_comments_number=5, scroll_before_click=True,
            #                                         number_of_scrolls=random.randint(2, 7)),
        ]
        # Randomly choose one action from the list
        return random.choice(random_actions)

    def run_actions(self):
        required_actions = [

            # MakeAccountPublicContext,
            # DeleteInitialPostsContext,
            # ChangeNameContext,
            # BrowserChangeUsernameEvent,
            # BrowserChangeAvatarEvent,
            RegisterEmailContext,

            # BrowserChangeBioEvent,
            # Activate2faCodeContext

            # GetContactInformationContext,
            # GetProfileScreenShotContext,

            # Daily actions
            # FollowContext,
            # SendDmWithPostContext,
            # CheckSystemUsernameWithIgUsernameContext,
            # GetLeadPkContext,
            # SendDmContext,

            # BrowserDmFollowUpEvent,
            # BrowserLoomFollowUpEvent,

            # Periodical actions
            # UnfollowContext,
            # FollowGoodPagesContext,
            # LeadGenerateByFollowersContext,
            # LeadGenerateByPageEngagementContext,
            # LeadGenerateByPostEngagementContext
        ]

        random.shuffle(required_actions)
        # events = required_actions + [self.select_random_explore_action()]
        events = required_actions

        for event in events:
            self.browser_ig.pause(1000, 3000)
            event(self.browser_ig).fire()
