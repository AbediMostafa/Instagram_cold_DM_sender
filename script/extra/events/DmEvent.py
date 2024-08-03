import traceback
from .BaseActionState import BaseActionState
from script.extra.actions.DM import DM
from script.extra.helper import pause
from script.extra.helper import test_accounts


class DmEvent(BaseActionState):
    dm = None

    def cant(self):
        return not self.dm.can_send_dm_today

    def init_state(self):
        self.account.add_cli("Starting DM process")
        self.dm = DM(self.account)
        self.dm.calculate_today_dms()

    def cant_state(self):
        text = f"We can't send DM for account : {self.account.username}"
        self.account.add_cli(text)
        self.account.add_log(text)

        return False

    def send_dm(self, lead):
        if not lead.instagram_id:
            self.account.add_cli(f"This lead don't has instagram_id : {lead.username}")
            lead.delete_instance()
            return False

        self.account.add_cli(f"Sending Dm to : {lead.username}")
        self.command = self.account.create_command('dm follow up', 'processing', lead)
        direct = self.ig.direct_send([lead.instagram_id], lead.dm_text)
        self.account.add_direct(lead.dm_text, lead, direct)

        lead.change_state(self.account, 'dm follow up', add_history=True, update_date=True)
        self.command.update_cmd('state', 'success')

    def success_state(self):
        self.account.set_state('sending DM', 'app_state')

        # for lead in test_accounts():
        for lead in self.dm.leads_to_send_cold_dm():
            self.get_lead_id(lead)
            pause(3, 5)
            self.send_dm(lead)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem sending cold dm: {str(e)}")
        self.account.add_log(traceback.format_exc())
