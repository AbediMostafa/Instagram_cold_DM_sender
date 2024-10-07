from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin
from script.extra.actions.DM import DM
from script.models.Lead import Lead
from peewee import fn
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent


class BrowserSendDmEvent(InstagramMiddleware):
    dm = None
    command = None
    allowed_leads_count = None
    base = None

    def execute(self):
        self.base = BrowserBaseEvent(self.ig)
        self.base.go_to_threads()
        self.init()

    def init(self):
        self.ig.account.add_cli("Starting DM process ...")
        self.dm = DM(self.ig.account)
        self.dm.calculate_today_dms()

        if not self.dm.can_send_dm_today:
            self.ig.account.add_cli("We can't send DM today")
            return

        self.allowed_leads_count = self.dm.chunk_dm
        self.ig.account.add_cli(f"Allowed leads count is {self.allowed_leads_count}")

        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')

        while self.allowed_leads_count > 0:
            lead = Lead.select().where(Lead.account.is_null()).order_by(fn.Rand()).first()
            lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

            self.send_dm(lead)
            self.ig.pause(3000, 6000)
            self.allowed_leads_count -= 1

    def send_dm(self, lead):

        try:
            self.ig.account.add_cli(f"Sending Dm to : {lead.username}")
            self.command = self.ig.account.create_command('dm follow up', 'processing', lead)
            self.send_direct(lead)
            self.ig.account.add_direct_url_id(lead.dm_text, lead, self.base.get_thread_id())

            lead.change_state(self.ig.account, 'dm follow up', add_history=True, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")
            lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)

            if self.command:
                self.command.update_cmd('state', 'fail')

    def send_direct(self, lead):
        self.ig.page.get_by_role("button", name="New message", exact=True).click(timeout=3000)
        self.ig.pause(3000, 4500)
        self.ig.page.get_by_placeholder("Search...").fill(lead.username)
        self.ig.pause(4000, 6000)

        try:
            self.ig.page.click(f'//text()[contains(., "{lead.username}")]/ancestor::div[@role="button"]', timeout=3000)
        except Exception as e:
            self.ig.page.reload()
            self.ig.pause(4000, 5000)
            self.ig.account.add_cli(f"User does not exists, deleting command ...")
            self.command.delete_instance()
            self.ig.account.add_cli(f"Command deleted successfully, raising exception ...")
            raise e

        self.ig.pause(3000, 5500)
        self.ig.page.get_by_role("button", name="Chat").click()
        self.ig.pause(3000, 4500)
        self.ig.page.get_by_label("Message", exact=True).fill(lead.dm_text)
        self.ig.pause(4000, 6000)
        self.ig.page.get_by_role("button", name="Send", exact=True).click()
        self.ig.pause(4000, 6000)
