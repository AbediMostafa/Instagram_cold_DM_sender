import random
from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction


class CanGenerateLeadByFollowers:
    def __init__(self, account):
        self.account = account

    def can(self):
        hours = random.randint(50, 90)
        performed_commands = performed_command_count(self.account, ['generate lead by followers'], hours)

        if performed_commands > 1:
            self.account.add_cli(f'We have generated leads by followers withing past {hours} hours')
            raise CantPerformAction(f'We have generated leads by followers withing past {hours} hours')
