from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.DmFollowUp import DmFollowUp
from script.models.Thread import get_url_id
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
import random


class BrowserDmFollowUpEvent(InstagramMiddleware):
    dm = None
    command = None
    leads = None
    url_id = None

    def execute(self):
        self.base.go_to_threads()
        self.ig.pause(2000, 3000)
        self.ig.turn_on_notif()
        self.init()

    def init(self):
        self.ig.account.add_cli("Starting DM Follow up process ...")
        self.dm = DmFollowUp(self.ig.account)
        cnt = random.randint(12, 17) if self.ig.account.has_enough_posts else 2
        self.leads = self.dm.leads_to_send_dm_follow_ups(cnt)

        if not len(self.leads):
            return self.ig.account.add_cli("There is no lead to follow up")

        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')

        for lead in self.leads:
            self.ig.account.add_cli(f"Sending Dm follow up to : {lead.username}")
            self.send_dm(lead)
            self.ig.pause(10000, 20000)

    def send_dm(self, lead):

        try:
            times = lead.times + 1
            self.command = self.ig.account.create_command('dm follow up', 'processing', lead, times)

            self.base.send_direct(lead, direct_url_id=get_url_id(lead, self.ig.account))
            self.ig.account.add_direct_url_id(lead.dm_text, lead, self.url_id)

            lead.change_state(self.ig.account, 'dm follow up', add_history=True, times=times, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")

            if self.command:
                self.command.update_cmd('state', 'fail')

            if str(e) == "Something went wrong":
                raise Exception(str(e))
