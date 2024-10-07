import traceback
from .BaseActionState import BaseActionState
from script.extra.actions.LoomFollowUp import LoomFollowUp
from script.extra.helper import pause


class LoomFollowUpEvent(BaseActionState):
    dm = None
    leads = None

    def cant(self):
        return not len(self.leads)

    def init_state(self):
        self.account.add_cli("Starting Loom follow up process")
        self.dm = LoomFollowUp(self.account)
        self.leads = self.dm.leads_to_send_loom_follow_ups()

    def cant_state(self):
        text = f"There is no lead to do loom follow up"
        self.account.add_cli(text)
        self.account.add_log(text)

        return False

    def send_dm(self, lead):

        if not lead.instagram_id:
            self.account.add_cli(f"This lead don't has instagram_id : {lead.username}")
            return False

        self.account.add_cli(f"Sending Loom follow up to : {lead.username}")

        times = lead.times + 1
        self.command = self.account.create_command('loom follow up', 'processing', lead, times)
        direct = self.ig.direct_send([lead.instagram_id], lead.dm_text)

        self.account.add_direct_url_id(lead.dm_text, lead)

        lead.change_state(self.account, 'loom follow up', add_history=True, times=times, update_date=True)
        self.command.update_cmd('state', 'success')

    def success_state(self):
        self.account.set_state('loom follow up', 'app_state')

        for lead in self.leads:
            pause(3, 5)
            self.get_lead_id(lead)
            self.send_dm(lead)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem Loom Follow up: {str(e)}")
        self.account.add_log(traceback.format_exc())
