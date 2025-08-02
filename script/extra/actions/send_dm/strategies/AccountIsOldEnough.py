from script.extra.exceptions import CantPerformAction


class AccountIsOldEnough:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        pass
        # if self.account.get_passed_days_since_creation() < 5:
        #     self.account.add_cli("It's not time to send dm")
        #     raise CantPerformAction("It's not time to send dm")
