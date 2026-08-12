from script.models.Command import sent_recent_command_within
from script.extra.exceptions import CantPerformAction
import random


class CanFollowToday:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        hours = random.randint(60, 80)
        had_successful_command = sent_recent_command_within(self.account, ['follow good pages'], hours)

        if had_successful_command:
            self.account.add_cli(f'We had Successful follow withing past {hours} hours')
            raise CantPerformAction(f'We had Successful follow withing past {hours} hours')
