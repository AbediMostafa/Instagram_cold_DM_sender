from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.Command import performed_command_count

from script.models.Command import Command
from script.models.Lead import Lead
from datetime import datetime, timedelta
from peewee import fn
from spintax import spin
import random


class DM:
    account = None
    can_send_dm_today = None
    chunk_dm = None

    def __init__(self, account):
        self.account = account

    def number_of_dm_strategy(self):
        passed_days = self.account.passed_days_since_creation
        max_dm = SettingAdapter.max_dm()
        max_dm = random.randint(max_dm - 4, max_dm + 4)

        allowed_dm = passed_days + 5 if passed_days < 7 else max_dm

        self.account.add_cli(f"Today's allowed dms : {allowed_dm}")

        return allowed_dm

    def sent_dm_within_passed_24hours(self):
        dm_command_count = performed_command_count(self.account, ['dm follow up'], 24)

        self.account.add_cli(f"We have sent {dm_command_count} DMs in the past 24 hours")

        return dm_command_count

    def calculate_today_dms(self):
        count = self.number_of_dm_strategy() - self.sent_dm_within_passed_24hours()
        dm_chunk = SettingAdapter.dm_chunk()

        self.can_send_dm_today = 0 if count < 1 else count
        self.account.add_cli(f"We can finally send {self.can_send_dm_today} DMs today")

        if self.can_send_dm_today:
            if self.can_send_dm_today > dm_chunk:
                lower_digit = 1 if (dm_chunk - 4) < 1 else dm_chunk - 4
                higher_digit = dm_chunk + 3
                self.chunk_dm = random.randint(lower_digit, higher_digit)

            else:
                lower_digit = 1 if (self.can_send_dm_today - 3) < 1 else self.can_send_dm_today - 3
                higher_digit = self.can_send_dm_today + 1
                self.chunk_dm = random.randint(lower_digit, higher_digit)

            self.account.add_cli(f"Chunk to send DM {self.chunk_dm}")

            return self.chunk_dm

        return self.can_send_dm_today

    def leads_to_send_cold_dm(self):
        leads = Lead.select().where(Lead.account.is_null()).limit(self.chunk_dm)

        self.account.add_cli(
            f'We have {leads.count()} leads to sent Cold DM')

        for lead in leads:
            lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

        return leads
