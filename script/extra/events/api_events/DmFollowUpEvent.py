import traceback
from .BaseActionState import BaseActionState
from script.extra.actions.DmFollowUp import DmFollowUp
from script.extra.helper import pause,test_accounts


class DmFollowUpEvent(BaseActionState):
    dm = None
    leads = None

    def cant(self):
        return not len(self.leads)

    def init_state(self):
        self.account.add_cli("Starting DM follow up process")
        self.dm = DmFollowUp(self.account)
        self.leads = self.dm.leads_to_send_dm_follow_ups()

    def cant_state(self):
        text = f"There is no lead to follow up"
        self.account.add_cli(text)
        self.account.add_log(text)

        return False

    def send_dm(self, lead):

        if not lead.instagram_id:
            self.account.add_cli(f"This lead don't has instagram_id : {lead.username}")
            return False

        self.account.add_cli(f"Sending Dm follow up to : {lead.username}")

        times = lead.times + 1
        self.command = self.account.create_command('dm follow up', 'processing', lead, times)
        direct = self.ig.direct_send([lead.instagram_id], lead.dm_text)

        self.account.add_direct_url_id(lead.dm_text, lead)

        lead.change_state(self.account, 'dm follow up', add_history=True, times=times, update_date=True)
        self.command.update_cmd('state', 'success')

    def success_state(self):
        self.account.set_state('sending DM', 'app_state')

        # for lead in test_accounts():
        for lead in self.leads:
            pause(3, 5)
            self.get_lead_id(lead)
            self.send_dm(lead)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem Following up the lead: {str(e)}")
        self.account.add_log(traceback.format_exc())
