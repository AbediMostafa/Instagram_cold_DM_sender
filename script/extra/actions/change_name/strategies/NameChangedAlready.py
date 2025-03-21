from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction
from script.extra.helper import calculate_daily_dms
import random


class NameChangedAlready:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):

        if self.account.has('name'):
            self.account.add_cli("Account has a name already")
            raise CantPerformAction("Account has a name already")
