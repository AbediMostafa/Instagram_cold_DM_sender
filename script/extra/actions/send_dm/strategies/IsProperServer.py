from script.extra.exceptions import IsNotProperServer
from script.models.Setting import Setting


class IsProperServer:
    def __init__(self, account):
        self.account = account

    def can(self):
        if Setting.get_value('can_send_dm') == "0":
            raise IsNotProperServer('This server cant send dm')
