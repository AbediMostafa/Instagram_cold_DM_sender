from script.extra.exceptions import IsNotProperServer
from script.models.Setting import Setting


class IsProperServer:
    def __init__(self, account):
        self.account = account

    def can(self):
        if not Setting.get_value('can_generate_lead_by_followers'):
            raise IsNotProperServer('This server cant generate lead by followers')
