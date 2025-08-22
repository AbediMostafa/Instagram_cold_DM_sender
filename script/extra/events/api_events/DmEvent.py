import traceback
from .BaseActionState import BaseActionState
from script.extra.helper import pause
from script.models.Lead import Lead
from script.models.DmPost import get_dm_post_for_lead
from script.models.Spintax import Spintax
from spintax import spin


class DmEvent(BaseActionState):
    dm = None
    leads = None
    dm_post = None
    dm_text = None
    commands = []
    lead_pks = []

    def cant(self):
        if self.account.current_chunk_dm is None:
            self.account.calculate_today_dms()

        if self.account.current_chunk_dm < 1:
            self.account.add_cli(
                f"We're not allowed to send DM, sent : {self.account.todays_sent_dms} allowed : {self.account.allowed_number_of_dms}")
            return True

        return False

    def init_state(self):
        self.account.add_cli("Starting DM process")
        self.dm_post = get_dm_post_for_lead(priority=0)
        self.dm_text = spin(Spintax.get_value(times=0))

        self.commands = []
        self.lead_pks = []

    def cant_state(self):
        pass

    def success_state(self):
        self.account.set_state('sending DM', 'app_state')
        self.get_leads()
        self.send_dm()

    def send_dm(self):

        for lead in self.leads:

            self.get_lead_id(lead)

            if not lead.instagram_id:
                self.account.add_cli(f"This lead don't has instagram_id : {lead.username}")
                lead.delete_instance()
                continue

            self.account.add_cli(f"Sending Dm to : {lead.username}")
            self.command = self.account.create_command('dm follow up', 'processing', lead)
            self.ig.media_share(self.dm_post.media_id, [lead.instagram_id])
            direct = self.ig.direct_send([lead.instagram_id], self.dm_text)
            self.account.add_direct(self.dm_text, lead, direct)
            lead.change_state(self.account, 'dm follow up', add_history=True, update_date=True)
            self.command.update_cmd('state', 'success')


    def get_leads(self):
        self.leads = Lead.get_leads_for_api_dm(self.account.current_chunk_dm)

        count = self.leads.count()
        self.account.add_cli(f'There are {count} leads with instagram_id ... ')

        if count != self.account.current_chunk_dm:
            return self.leads

        self.account.add_cli('Warning =============================================')
        self.account.add_cli(f'There is not enough leads with instagram_id getting normal leads ...')
        self.account.add_cli('=====================================================')

        self.leads = Lead.get_leads_for_dm(self.account, self.account.current_chunk_dm)

    def exception_state(self, e):
        self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem sending cold dm: {str(e)}")
        self.account.add_log(traceback.format_exc())
