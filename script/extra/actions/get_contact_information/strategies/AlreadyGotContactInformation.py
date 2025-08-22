from script.models.Command import sent_recent_command_within
from script.extra.exceptions import CantPerformAction
import random


class AlreadyGotContactInformation:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        if self.account.phone:
            self.account.add_cli("Contact information got already")
            raise CantPerformAction("Contact information got already")
