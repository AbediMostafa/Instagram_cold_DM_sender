import random
from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction


class CanGenerateLeadByPageEngagement:
    def __init__(self, account):
        self.account = account

    def can(self):
        hours = random.randint(40, 80)
        performed_commands = performed_command_count(self.account, ['generate lead by page engagement'], hours)

        if performed_commands > 1:
            self.account.add_cli(f'We have generated leads by page engagement withing past {hours} hours')
            raise CantPerformAction(f'We have generated leads by page engagement withing past {hours} hours')
