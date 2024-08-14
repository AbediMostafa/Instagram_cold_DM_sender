from datetime import datetime, timedelta
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.extra.helper import pause


class CheckForLastLoginHook:

    def __init__(self, account):
        self.account = account

    def next_login_not_reached(self):
        self.account.add_cli("Checking for next login")
        next_login_has_not_reached, time_delta = self.account.next_login_has_not_reached_yet()

        if next_login_has_not_reached:
            self.account.add_cli(f"{time_delta.total_seconds()//3600} hours remains for next login")
            pause(4, 8)
            return True

        return False
