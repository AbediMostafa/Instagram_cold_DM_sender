from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.Lead import Lead
from datetime import datetime, timedelta
from spintax import spin
from script.extra.adapters.LoomFollowUpAdapter import LoomFollowUpAdapter


class LoomFollowUp:
    account = None
    chunk_dm = None

    def __init__(self, account):
        self.account = account
        self.chunk_dm = SettingAdapter.dm_chunk()

    def leads_to_send_loom_follow_ups(self):
        forty_eight_hours_ago = datetime.now() - timedelta(hours=48)

        leads = Lead.select().where(
            (Lead.last_state == 'loom follow up') &
            (Lead.account == self.account) &
            (Lead.times < 11) &
            (Lead.last_command_send_date < forty_eight_hours_ago)
        ).limit(self.chunk_dm)

        self.account.add_cli(f'We have {len(leads)} leads for loom follow up')
        text = LoomFollowUpAdapter.loom_text()

        for lead in leads:
            lead.dm_text = text[lead.times]

        return leads
