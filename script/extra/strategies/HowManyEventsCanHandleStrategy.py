import random
from script.extra.events.ChangeNameEvent import ChangeNameEvent
from script.extra.events.ChangeUsernameEvent import ChangeUsernameEvent
from script.extra.events.ChangeAvatarEvent import ChangeAvatarEvent
from script.extra.events.ChangeBioEvent import ChangeBioEvent
from script.extra.events.FollowEvent import FollowEvent
from script.extra.events.DmEvent import DmEvent
from script.extra.events.PostImageEvent import PostImageEvent
from script.extra.events.PostVideoEvent import PostVideoEvent
from script.extra.events.DmFollowUpEvent import DmFollowUpEvent
from script.extra.events.LoomFollowUpEvent import LoomFollowUpEvent
from script.extra.events.DeleteInitialPostsEvent import DeleteInitialPostsEvent
from script.extra.events.LikeAndCommentLeadsPosts import LikeAndCommentLeadsPosts
from script.extra.events.LikeAndCommentFeeds import LikeAndCommentFeeds
from script.extra.helper import pause


class HowManyEventsCanHandleStrategy:
    account = None
    ig = None
    events = None
    passed_days = None
    event_count = None

    def __init__(self, account, ig):
        self.account = account
        self.ig = ig

        self.account.get_passed_days_since_creation()
        self.account.add_cli(f'We are at the {self.account.passed_days_since_creation} day of account creation')

    def run(self):
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
            pause(18, 40)
            # pause(3, 6)
            event.fire()

    def first_day_strategy(self):
        self.account.add_cli('running first day strategy')
        self.events = [
            # DeleteInitialPostsEvent(self.account, self.ig),
            ChangeUsernameEvent(self.account, self.ig),
            FollowEvent(self.account, self.ig),
            LikeAndCommentFeeds(self.account, self.ig),
            LikeAndCommentLeadsPosts(self.account, self.ig),
        ]

    def second_day_strategy(self):
        self.account.add_cli('running second day strategy')

        self.events = [
            DeleteInitialPostsEvent(self.account, self.ig),
            ChangeUsernameEvent(self.account, self.ig),

            # ChangeNameEvent(self.account, self.ig),
            FollowEvent(self.account, self.ig),
            DmEvent(self.account, self.ig),
            LikeAndCommentFeeds(self.account, self.ig),
            LikeAndCommentLeadsPosts(self.account, self.ig),
        ]

    def third_day_strategy(self):
        self.account.add_cli('running third day strategy')

        self.events = [
            DeleteInitialPostsEvent(self.account, self.ig),
            ChangeUsernameEvent(self.account, self.ig),
            #             ChangeNameEvent(self.account, self.ig),

            ChangeAvatarEvent(self.account, self.ig),
            ChangeBioEvent(self.account, self.ig),
            FollowEvent(self.account, self.ig),
            DmEvent(self.account, self.ig),
            LikeAndCommentFeeds(self.account, self.ig),
            LikeAndCommentLeadsPosts(self.account, self.ig),
        ]

    def fourth_day_strategy(self):
        self.account.add_cli('running fourth day strategy')

        self.events = [
            ChangeUsernameEvent(self.account, self.ig),
            #             ChangeNameEvent(self.account, self.ig),
            ChangeAvatarEvent(self.account, self.ig),
            ChangeBioEvent(self.account, self.ig),

            PostImageEvent(self.account, self.ig),
            FollowEvent(self.account, self.ig),
            DmEvent(self.account, self.ig),
            DmFollowUpEvent(self.account, self.ig),
            LoomFollowUpEvent(self.account, self.ig),
            LikeAndCommentFeeds(self.account, self.ig),
            LikeAndCommentLeadsPosts(self.account, self.ig),
        ]

    def fifth_day_strategy(self):
        self.account.add_cli('running fifth day strategy')

        self.events = [
            ChangeUsernameEvent(self.account, self.ig),
            #             ChangeNameEvent(self.account, self.ig),
            ChangeAvatarEvent(self.account, self.ig),
            ChangeBioEvent(self.account, self.ig),

            PostImageEvent(self.account, self.ig),
            PostVideoEvent(self.account, self.ig),
            FollowEvent(self.account, self.ig),
            DmEvent(self.account, self.ig),
            DmFollowUpEvent(self.account, self.ig),
            LoomFollowUpEvent(self.account, self.ig),
            LikeAndCommentFeeds(self.account, self.ig),
            LikeAndCommentLeadsPosts(self.account, self.ig),
        ]

    def more_than_five_days_strategy(self):
        self.account.add_cli('running more than five days strategy')

        self.events = [
            DeleteInitialPostsEvent(self.account, self.ig),
            ChangeAvatarEvent(self.account, self.ig),
            ChangeUsernameEvent(self.account, self.ig),

            PostImageEvent(self.account, self.ig),
            PostVideoEvent(self.account, self.ig),
            FollowEvent(self.account, self.ig),
            DmEvent(self.account, self.ig),
            DmFollowUpEvent(self.account, self.ig),
            LoomFollowUpEvent(self.account, self.ig),
            LikeAndCommentFeeds(self.account, self.ig),
            LikeAndCommentLeadsPosts(self.account, self.ig),
        ]
