from datetime import datetime, timedelta
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.extra.helper import pause


class CheckForWarningsHook:

    def __init__(self, account):
        self.account = account

    def last_warning_has_not_expired(self):
        self.account.add_cli("Checking for account's warning expiry... ")

        warning = self.account.get_latest_warning()

        if warning:
            if warning.expiration_time_not_passed():
                self.account.add_cli(f'We have a {warning.cause} warning for the account')
                self.account.add_cli(f'{warning.get_hours_until_expiry()} hours remains until account relief')
                pause(3, 8)
                return True

        return False
