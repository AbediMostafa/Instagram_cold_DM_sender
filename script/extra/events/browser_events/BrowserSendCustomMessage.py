from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin
from script.extra.actions.DM import DM
from script.models.Lead import Lead
from peewee import fn
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Thread import get_url_id


class BrowserSendCustomMessage(InstagramMiddleware):
    dm = None
    command = None
    base = None
    message = None

    def execute(self):
        self.base.go_to_threads()
        self.ig.turn_on_notif()
        self.init()

    def init(self):
        self.ig.account.add_cli("Starting Sending Custom message process ...")
        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')

        for self.command in self.ig.account.custom_message_commands:
            lead = self.command.lead
            self.message = self.command.get_commandable()
            lead.dm_text = self.message.text

            self.send_dm(lead)
            self.ig.pause(7000, 12000)

    def send_dm(self, lead):

        try:
            self.ig.account.add_cli(f"Sending Custom message to : {lead.username}")
            self.base.send_direct(lead, direct_url_id=get_url_id(lead, self.ig.account))

            if self.command.type == 'send loom':
                lead.change_state(self.ig.account, 'loom follow up', add_history=True, update_date=True)

            self.message.update_state('seen')
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")
            # lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)

            if self.command:
                self.command.update_cmd('state', 'fail')

            if str(e) == "Something went wrong":
                raise Exception(str(e))
