from datetime import datetime
from script.extra.helper import tehran_now


class RecordLastActivityHook:
    def __init__(self, account):
        self.account = account
        self.update_last_activity()

    def update_last_activity(self):
        new_time = self.account.update_last_activity()

        # Calculate the time difference in hours
        hours = round((new_time - tehran_now()).total_seconds() / 3600, 2)
        self.account.add_cli(f"Account will start {hours} hours later")
