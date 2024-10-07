from script.extra.adapters.SettingAdapter import SettingAdapter

from script.models.Lead import Lead
from datetime import datetime, timedelta
from spintax import spin
import random


class DmFollowUp:
    account = None
    chunk_dm = None

    def __init__(self, account):
        self.account = account
        self.chunk_dm = SettingAdapter.dm_chunk()

    def leads_to_send_dm_follow_ups(self):
        forty_eight_hours_ago = datetime.now() - timedelta(hours=48)

        leads = Lead.select().where(
            (Lead.last_state == 'dm follow up') &
            (Lead.account == self.account) &
            (Lead.times < 3) &
            (Lead.last_command_send_date < forty_eight_hours_ago)
        ).limit(random.randint(25,40))

        self.account.add_cli(f'We have {len(leads)} leads for follow up')

        for lead in leads:
            if lead.times == 0:
                lead.dm_text = spin(SettingAdapter.first_dm_follow_up_spintax(self.account))

            if lead.times == 1:
                lead.dm_text = spin(SettingAdapter.second_dm_follow_up_spintax(self.account))

            if lead.times == 2:
                lead.dm_text = spin(SettingAdapter.third_dm_follow_up_spintax(self.account))

        return leads
