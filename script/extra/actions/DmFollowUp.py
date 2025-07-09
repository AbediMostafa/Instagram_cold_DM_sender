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
        self.leads = []

    def leads_to_send_dm_follow_ups(self, cnt):

        leads = Lead.select().where(
            (Lead.last_state == 'dm follow up') &
            (Lead.account == self.account)
            # (Lead.last_command_send_date > hours_ago(172))
        )

        for lead in leads:

            if not lead.category:
                self.account.add_cli(f'{lead.username} dont have category')
                continue

            if lead.has_not_reached_dm_send_time_yet():
                continue

            spintax = Spintax.get_value(lead.times + 1, lead.category)


            if not spintax:
                continue

            lead.dm_text = spin(spintax)
            self.leads.append(lead)

            self.counter += 1

            if self.counter >= cnt:
                return self.leads

        return self.leads
