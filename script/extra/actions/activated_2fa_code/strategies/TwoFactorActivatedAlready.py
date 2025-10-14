from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction
from script.extra.helper import calculate_daily_dms
import random


class TwoFactorActivatedAlready:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):

        if self.account.two_factor_activated:
            self.account.add_cli("Two factor activated already")
            raise CantPerformAction("Two factor activated already")
