from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction
from script.extra.helper import calculate_daily_dms
import random


class InitialPostsDeletedAlready:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):

        if self.account.initial_posts_deleted:
            self.account.add_cli("Initial posts deleted already")
            raise CantPerformAction("Initial posts deleted already")
