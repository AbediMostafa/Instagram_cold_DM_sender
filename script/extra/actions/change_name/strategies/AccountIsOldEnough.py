from script.extra.exceptions import CantPerformAction


class AccountIsOldEnough:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        if self.account.get_passed_days_since_creation() < 2:
            self.account.add_cli("It's not time to change the account's name.")
            raise CantPerformAction("It's not time to change the account's name.")
