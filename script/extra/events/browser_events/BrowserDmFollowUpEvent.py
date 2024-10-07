from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.DmFollowUp import DmFollowUp
from script.models.Thread import get_url_id
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent


class BrowserDmFollowUpEvent(InstagramMiddleware):
    dm = None
    command = None
    leads = None
    url_id = None
    base = None

    def execute(self):
        self.base = BrowserBaseEvent(self.ig)
        self.base.go_to_threads()
        self.init()

    def init(self):
        self.ig.account.add_cli("Starting DM Follow up process ...")
        self.dm = DmFollowUp(self.ig.account)
        self.leads = self.dm.leads_to_send_dm_follow_ups()

        if not len(self.leads):
            return self.ig.account.add_cli("There is no lead to follow up")

        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')

        for lead in self.leads:
            self.ig.account.add_cli(f"Sending Dm follow up to : {lead.username}")
            self.send_dm(lead)
            self.ig.pause(3000, 5000)

    def send_dm(self, lead):

        try:
            times = lead.times + 1
            self.command = self.ig.account.create_command('dm follow up', 'processing', lead, times)

            self.send_direct(lead)
            self.ig.account.add_direct_url_id(lead.dm_text, lead, self.url_id)

            lead.change_state(self.ig.account, 'dm follow up', add_history=True, times=times, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")
            lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)

            if self.command:
                self.command.update_cmd('state', 'fail')

    def send_direct(self, lead):
        self.url_id = get_url_id(lead, self.ig.account)

        if not self.url_id:
            raise Exception("Thread dont have url_id")

        self.ig.page.goto(f'https://www.instagram.com/direct/t/{self.url_id}/')

        self.ig.pause(4000, 4500)
        self.ig.page.get_by_label("Message", exact=True).fill(lead.dm_text)
        self.ig.pause(3000, 5000)
        self.ig.page.get_by_role("button", name="Send", exact=True).click()
        self.ig.pause(3000, 5000)
