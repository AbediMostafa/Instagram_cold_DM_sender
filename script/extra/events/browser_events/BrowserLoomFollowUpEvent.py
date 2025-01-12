from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.LoomFollowUp import LoomFollowUp
from script.models.Thread import get_url_id
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent


class BrowserLoomFollowUpEvent(InstagramMiddleware):
    dm = None
    command = None
    leads = None
    url_id = None
    base = None

    def execute(self):
        self.ig.account.add_cli("Starting Loom Follow up process ...")
        self.dm = LoomFollowUp(self.ig.account)
        self.leads = self.dm.leads_to_send_loom_follow_ups()

        if not len(self.leads):
            return self.ig.account.add_cli("There is no lead to loom follow up")

        self.base.go_to_threads()
        self.ig.turn_on_notif()

        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('loom follow up', 'app_state')

        for lead in self.leads:
            self.ig.account.add_cli(f"Sending Dm follow up to : {lead.username}")
            self.send_dm(lead)
            self.ig.pause(8000, 12000)

    def send_dm(self, lead):

        try:
            times = lead.times + 1
            self.command = self.ig.account.create_command('loom follow up', 'processing', lead, times)

            self.base.send_direct(lead, direct_url_id=get_url_id(lead, self.ig.account))
            self.ig.account.add_direct_url_id(lead.dm_text, lead)

            lead.change_state(self.ig.account, 'loom follow up', add_history=True, times=times, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send Loom follow up : {str(e)}")
            # lead.change_state(self.ig.account, 'failed loom dm', add_history=True, update_date=True)

            if self.command:
                self.command.update_cmd('state', 'fail')

            if str(e) == "Something went wrong":
                raise Exception(str(e))
