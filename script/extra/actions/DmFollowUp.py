from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.Lead import Lead
from script.models.Spintax import Spintax
from spintax import spin
from script.extra.helper import hours_ago
from script.extra.helper import tehran_now


class DmFollowUp:
    account = None
    chunk_dm = None
    counter = 0
    leads = []

    def __init__(self, account):
        self.account = account
        self.chunk_dm = SettingAdapter.dm_chunk()

    def leads_to_send_dm_follow_ups(self, cnt):
        forty_eight_hours_ago = hours_ago(72)

        leads = Lead.select().where(
            (Lead.last_state == 'dm follow up') &
            (Lead.account == self.account) &
            (Lead.last_command_send_date < forty_eight_hours_ago)
        )

        for lead in leads:

            if not lead.category:
                self.account.add_cli(f'{lead.username} dont have category')
                continue

            if lead.has_not_reached_dm_send_time_yet():
                continue

            self.counter += 1

            lead.dm_text = Spintax.get_value(lead.times + 1, lead.category)
            self.leads.append(lead)

            if self.counter >= cnt:
                return self.leads

        return self.leads
