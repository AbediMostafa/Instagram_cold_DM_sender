from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin
from script.models.Lead import Lead


class BrowserSendDmEvent(InstagramMiddleware):
    dm = None
    command = None
    allowed_leads_count = None
    base = None

    def execute(self):

        # if not self.ig.account.has_enough_posts:
        #     self.ig.account.add_cli("Account dont have enough post to send DM")
        #     return

        if self.ig.account.final_allowed_number_of_dms < 1:
            self.ig.account.add_cli("We can't send DM today")
            return

        self.base.go_to_threads()
        self.ig.turn_on_notif()
        self.init()

    def init(self):
        self.ig.account.add_cli("Starting DM process ...")

        self.allowed_leads_count = self.ig.account.current_chunk_dm
        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')

        while self.allowed_leads_count > 0:
            lead = Lead.get_leads()[0]
            lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

            self.send_dm(lead)
            self.ig.pause(7000, 12000)
            self.allowed_leads_count -= 1

    def send_dm(self, lead):

        try:
            self.ig.account.add_cli(f"Sending Dm to : {lead.username}")
            self.command = self.ig.account.create_command('dm follow up', 'processing', lead)
            self.base.send_direct(lead)
            self.ig.account.add_direct_url_id(lead.dm_text, lead, self.base.get_thread_id())

            lead.change_state(self.ig.account, 'dm follow up', add_history=True, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")
            # lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)

            if self.command:
                self.command.update_cmd('state', 'fail')

            if str(e) == "Something went wrong":
                raise Exception(str(e))
