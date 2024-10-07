import random

from script.extra.events.api_events.ChangeNameEvent import ChangeNameEvent
from script.extra.events.api_events.ChangeUsernameEvent import ChangeUsernameEvent
from script.extra.events.api_events.ChangeAvatarEvent import ChangeAvatarEvent
from script.extra.events.api_events.ChangeBioEvent import ChangeBioEvent
from script.extra.events.api_events.FollowEvent import FollowEvent
from script.extra.events.api_events.DmEvent import DmEvent
from script.extra.events.api_events.PostImageEvent import PostImageEvent
from script.extra.events.api_events.PostVideoEvent import PostVideoEvent
from script.extra.events.api_events.DmFollowUpEvent import DmFollowUpEvent
from script.extra.events.api_events.LoomFollowUpEvent import LoomFollowUpEvent
from script.extra.events.api_events.DeleteInitialPostsEvent import DeleteInitialPostsEvent
from script.extra.events.api_events.GetThreadMessagesEvent import GetThreadMessagesEvent
from script.extra.events.browser_events.BrowserScrollAndLikeEvent import BrowserScrollAndLikeEvent
from script.extra.events.browser_events.BrowserDeleteInitialPostsEvent import BrowserDeleteInitialPostsEvent
from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.events.browser_events.BrowserSendDmEvent import BrowserSendDmEvent
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.events.browser_events.BrowserLoomFollowUpEvent import BrowserLoomFollowUpEvent
from script.extra.events.browser_events.BrowserChangeBioEvent import BrowserChangeBioEvent
from script.extra.events.browser_events.BrowserChangeNameEvent import BrowserChangeNameEvent
from script.extra.events.browser_events.BrowserGetThreadMessagesEvent import BrowserGetThreadMessagesEvent
from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.events.browser_events.BrowserGoToTargetAccountAndExplorePosts import \
    BrowserGoToTargetAccountAndExplorePosts

from script.extra.helper import pause
from script.models.Command import Command
from datetime import datetime, timedelta


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
        self.account.get_passed_days_since_creation()
        self.account.add_cli(f'We are at the {self.account.passed_days_since_creation} day of account creation')

    def run(self):

        self.post_hook()

        """
        Sometimes, we have newly imported accounts with many actions to perform,
        such as following, sending DMs, changing usernames, etc.
        Performing all these actions can lead the account to be challenging.
        Therefore, we only execute actions based on the number of days since the account's creation date.
        For example, if an account was created yesterday, we perform 3 actions,
        and if the account was created two days ago, we perform only 4 actions.
        """
        strategies = {
            0: self.first_day_strategy,
            1: self.second_day_strategy,
            2: self.third_day_strategy,
            3: self.fourth_day_strategy,
            4: self.fifth_day_strategy,
            5: self.more_than_five_days_strategy,
        }

        offset = 5 if self.account.passed_days_since_creation > 5 else self.account.passed_days_since_creation
        strategies[offset]()
        random.shuffle(self.events)

        for event in self.events:
            pause(1, 3)
            event.fire()

    def post_hook(self):
        BrowserGetThreadMessagesEvent(self.browser_ig).fire()
        next_command = self.account.determine_next_post_command()

        if next_command == 'post carousel':
            self.account.add_cli('We should post carousel')
            BrowserPostCarouselEvent(self.browser_ig).fire()

        elif next_command == 'post video':
            self.account.add_cli('We should post video')
            PostVideoEvent(self.account).fire()

        elif next_command == 'post image':
            self.account.add_cli('We should post image')
            BrowserPostImageEvent(self.browser_ig).fire()

    def first_day_strategy(self):
        self.account.add_cli('running first day strategy')

        self.events = [
            BrowserDeleteInitialPostsEvent(self.browser_ig),

            BrowserGotoExploreEvent(self.browser_ig),
            BrowserSendDmEvent(self.browser_ig),
            BrowserScrollAndLikeEvent(self.browser_ig),
            BrowserGetThreadMessagesEvent(self.browser_ig)
        ]

    def second_day_strategy(self):
        self.account.add_cli('running second day strategy')

        self.events = [
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),

            BrowserGotoExploreEvent(self.browser_ig),
            BrowserSendDmEvent(self.browser_ig),
            BrowserScrollAndLikeEvent(self.browser_ig),
            BrowserGetThreadMessagesEvent(self.browser_ig),
        ]

    def third_day_strategy(self):
        self.account.add_cli('running third day strategy')

        self.events = [
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),

            BrowserGotoExploreEvent(self.browser_ig),
            BrowserSendDmEvent(self.browser_ig),
            BrowserScrollAndLikeEvent(self.browser_ig),

            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            BrowserGetThreadMessagesEvent(self.browser_ig)
        ]

    def fourth_day_strategy(self):
        self.account.add_cli('running fourth day strategy')
        self.events = [
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),
            BrowserChangeBioEvent(self.browser_ig),

            BrowserGotoExploreEvent(self.browser_ig),
            BrowserScrollAndLikeEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            BrowserGetThreadMessagesEvent(self.browser_ig),
        ]

    def fifth_day_strategy(self):
        self.account.add_cli('running fifth day strategy')

        self.events = [
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),
            BrowserChangeBioEvent(self.browser_ig),
            BrowserChangeNameEvent(self.browser_ig),

            BrowserGotoExploreEvent(self.browser_ig),
            BrowserScrollAndLikeEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            BrowserGetThreadMessagesEvent(self.browser_ig),

            # BrowserPostImageEvent(self.account),
        ]

    def more_than_five_days_strategy(self):
        self.account.add_cli('running more than five days strategy')

        self.events = [
            # BrowserDeleteInitialPostsEvent(self.browser_ig),
            # BrowserChangeUsernameEvent(self.browser_ig),
            # BrowserChangeAvatarEvent(self.browser_ig),
            # BrowserChangeBioEvent(self.browser_ig),
            # BrowserChangeNameEvent(self.browser_ig),
            # BrowserGetThreadMessagesEvent(self.browser_ig),
            BrowserGotoExploreEvent(self.browser_ig),
            BrowserScrollAndLikeEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),

            # BrowserGoToTargetAccountAndExplorePosts(self.browser_ig, user_type='lead',
            #                                         user_numbers=random.randint(1, 4),
            #                                         post_numbers=random.randint(1, 4),
            #                                         load_more_comments_number=5, scroll_before_click=True,
            #                                         number_of_scrolls=random.randint(6, 10)),
            # #
            # BrowserGoToTargetAccountAndExplorePosts(self.browser_ig, user_type='random_user',
            #                                         user_numbers=random.randint(1, 3),
            #                                         post_numbers=random.randint(1, 5),
            #                                         load_more_comments_number=5, scroll_before_click=True,
            #                                         number_of_scrolls=random.randint(2, 7)),
            #
            # BrowserGoToTargetAccountAndExplorePosts(self.browser_ig, user_type='random_user',
            #                                         user_numbers=random.randint(1, 3),
            #                                         post_numbers=random.randint(1, 5),
            #                                         load_more_comments_number=5, scroll_before_click=True,
            #                                         number_of_scrolls=random.randint(2, 7)),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
        ]
