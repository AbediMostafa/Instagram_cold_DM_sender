from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction
from script.extra.helper import calculate_daily_dms
import random


class CanUnfollowToday:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        hours = random.randint(40, 60)
        performed_commands = performed_command_count(self.account, ['unfollow'], hours)

        if performed_commands > 13:
            self.account.add_cli(f'We have unfollowed withing past {hours} hours')
            raise CantPerformAction(f'We have unfollowed withing past {hours} hours')