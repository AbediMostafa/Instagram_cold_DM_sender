from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction
from script.extra.helper import calculate_daily_dms
import random


class AccountIsPrivateAlready:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):

        if not self.account.is_public:
            self.account.add_cli("Account is private")
            raise CantPerformAction("Account is private")
