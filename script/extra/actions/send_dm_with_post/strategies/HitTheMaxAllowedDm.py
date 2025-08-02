from script.extra.exceptions import CantPerformAction
from script.models.Command import performed_command_count
from script.extra.helper import calculate_daily_dms


class HitTheMaxAllowedDm:

    def __init__(self, account):
        self.account = account

    def can(self):

        if self.account.current_chunk_dm is None:
            self.account.calculate_today_dms()

        if self.account.current_chunk_dm < 1:
            self.account.add_cli(
                f"We're not allowed to send DM wit Post, sent : {self.account.todays_sent_dms} allowed : {self.account.allowed_number_of_dms}")
            raise CantPerformAction("We're not allowed to send DM wit Post")

