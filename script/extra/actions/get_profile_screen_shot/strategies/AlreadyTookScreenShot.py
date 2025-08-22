from script.models.Command import sent_recent_command_within
from script.extra.exceptions import CantPerformAction
import random


class AlreadyTookScreenShot:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        if self.account.screenshot_taken:
            self.account.add_cli("Screen shot taken already")
            raise CantPerformAction("Screen shot taken already")
