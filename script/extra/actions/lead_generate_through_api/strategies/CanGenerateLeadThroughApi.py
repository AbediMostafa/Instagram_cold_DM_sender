import random
from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction


class CanGenerateLeadThroughApi:
    def __init__(self, account):
        self.account = account

    def can(self):
        hours = random.randint(40, 48)
        performed_commands = performed_command_count(self.account, ['explore hashtag'], hours)

        if performed_commands > 1:
            self.account.add_cli(f'We had Successful follow withing past {hours} hours')
            raise CantPerformAction(f'We had Successful follow withing past {hours} hours')
