import random

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
from script.extra.events.browser_events.BrowserSendCustomMessage import BrowserSendCustomMessage
from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
from script.extra.events.browser_events.BrowserPostVideoEvent import BrowserPostVideoEvent
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.events.browser_events.BrowserMakeAccountPublic import BrowserMakeAccountPublic
from script.extra.events.browser_events.BrowserSeeStories import BrowserSeeStories
from script.extra.events.browser_events.BrowserGoToTargetAccountAndExplorePosts import \
    BrowserGoToTargetAccountAndExplorePosts

from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import LeadGenerateThroughApiContext


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

        self.pre_action_hook()

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
            5: self.sixth_day_strategy,
            6: self.seventh_day_strategy,
            7: self.eighth_day_strategy,
            8: self.ninth_day_strategy,
            9: self.tenth_day_strategy,
            10: self.eleventh_day_strategy,
            11: self.other_days_strategy,
        }

        offset = 11 if self.account.passed_days_since_creation > 11 else self.account.passed_days_since_creation

        strategies[offset]()
        random.shuffle(self.events)

        for event in self.events:
            self.browser_ig.pause(1000, 3000)
            event.fire()

        self.post_action_hook()

    def pre_action_hook(self):
        BrowserSendCustomMessage(self.browser_ig).fire()
        BrowserGetThreadMessagesEvent(self.browser_ig).fire()

    def post_action_hook(self):
        if not self.account.has_enough_posts and self.account.initial_posts_deleted:
            self.account.add_cli('We can post now')
            self.post_a_media()

    def post_a_media(self):
        next_command = self.account.determine_next_post_command()

        if next_command == 'post carousel':
            self.account.add_cli('We should post carousel')
            BrowserPostCarouselEvent(self.browser_ig).fire()

        elif next_command == 'post video':
            self.account.add_cli('We should post video')
            BrowserPostVideoEvent(self.browser_ig).fire()

        elif next_command == 'post image':
            self.account.add_cli('We should post image')
            BrowserPostImageEvent(self.browser_ig).fire()

    def select_random_explore_action(self):
        # Define a list of random actions to choose from each day
        random_actions = [
            BrowserScrollAndLikeEvent(self.browser_ig),
            BrowserGotoExploreEvent(self.browser_ig),
            BrowserSeeStories(self.browser_ig),
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

    def first_day_strategy(self):
        self.account.add_cli('running first day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserSendDmEvent(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def second_day_strategy(self):
        self.account.add_cli('running second day strategy')

        required_actions = [
            BrowserSendDmEvent(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def third_day_strategy(self):
        self.account.add_cli('running third day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def fourth_day_strategy(self):
        self.account.add_cli('running fourth day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def fifth_day_strategy(self):
        self.account.add_cli('running fifth day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def sixth_day_strategy(self):
        self.account.add_cli('running sixth day strategy')
        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def seventh_day_strategy(self):
        self.account.add_cli('running seventh day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def eighth_day_strategy(self):
        self.account.add_cli('running eighth day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def ninth_day_strategy(self):
        self.account.add_cli('running ninth day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),
            BrowserChangeBioEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def tenth_day_strategy(self):
        self.account.add_cli('running tenth day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),
            BrowserChangeBioEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def eleventh_day_strategy(self):
        self.account.add_cli('running eleventh day strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),
            BrowserChangeBioEvent(self.browser_ig),
            BrowserChangeNameEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]

    def other_days_strategy(self):
        self.account.add_cli('running more than five days strategy')

        required_actions = [
            BrowserMakeAccountPublic(self.browser_ig),
            BrowserDeleteInitialPostsEvent(self.browser_ig),
            BrowserChangeUsernameEvent(self.browser_ig),
            BrowserChangeAvatarEvent(self.browser_ig),
            BrowserChangeBioEvent(self.browser_ig),
            BrowserChangeNameEvent(self.browser_ig),

            BrowserSendDmEvent(self.browser_ig),
            BrowserDmFollowUpEvent(self.browser_ig),
            BrowserLoomFollowUpEvent(self.browser_ig),
            LeadGenerateThroughApiContext(self.browser_ig),
        ]

        self.events = required_actions + [self.select_random_explore_action()]
