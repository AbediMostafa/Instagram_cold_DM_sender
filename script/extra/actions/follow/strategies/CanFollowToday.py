from script.models.Command import performed_command_count
from script.extra.exceptions import CantPerformAction
from script.extra.helper import calculate_daily_dms
import random


class CanFollowToday:
    account = None

    def __init__(self, account):
        self.account = account

    def can(self):
        allowed_follows = calculate_daily_dms(self.account.get_passed_days_since_creation())

        performed_follows = performed_command_count(
            self.account,
            ['follow good pages', 'follow'],
            24)

        if performed_follows >= allowed_follows:
            self.account.add_cli(f'We have had hit max number of allowed follows({allowed_follows})')
            raise CantPerformAction(f'We have had hit max number of allowed follows({allowed_follows})')
