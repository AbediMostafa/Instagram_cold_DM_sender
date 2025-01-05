import time
from datetime import datetime, timedelta
import random
from script.extra.adapters.SettingAdapter import SettingAdapter


class RecordLastActivityHook:
    def __init__(self, account):
        self.account = account
        self.update_last_activity()

    def update_last_activity(self):
        self.account.add_cli("Recording last activity time ...")
        new_time = self.account.update_last_activity()

        # Calculate the time difference in hours
        hours = round((new_time - datetime.now()).total_seconds() / 3600, 2)
        self.account.add_cli(f"Account will start {hours} hours later")
