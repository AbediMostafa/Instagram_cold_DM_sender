from script.extra.adapters.SettingAdapter import SettingAdapter

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
        allowed_dm = min(self.account.passed_days_since_creation+1, SettingAdapter.max_dm())

        self.account.add_cli(f"Today's allowed dms : {allowed_dm}")

        return allowed_dm

    def sent_dm_within_passed_24hours(self):
        twenty_hours_ago = datetime.now() - timedelta(hours=24)

        dm_command_count = (Command
                            .select(fn.COUNT(Command.id).alias('count'))
                            .where(
            (Command.account == self.account) &
            (Command.type.in_(['dm follow up'])) &
            (Command.times == 0) &
            (Command.state == 'success') &
            (Command.created_at >= twenty_hours_ago)
        )
                            .scalar())

        self.account.add_cli(f"We have sent {dm_command_count} DMs in the past 24 hours")

        return dm_command_count

    def calculate_today_dms(self):
        count = self.number_of_dm_strategy() - self.sent_dm_within_passed_24hours()

        self.can_send_dm_today = 0 if count < 1 else count
        self.account.add_cli(f"We can finally send {self.can_send_dm_today} DMs today")

        if self.can_send_dm_today:
            self.chunk_dm = min(self.can_send_dm_today, SettingAdapter.dm_chunk())
            self.chunk_dm = random.randint(1, self.chunk_dm)
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
