from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.playwright.base_actions.GoToThreadsAction import GoToThreadsAction
from script.extra.playwright.base_actions.TurnOnNotificationAction import TurnOnNotificationAction
from script.extra.playwright.base_actions.ClickOnNewMessageAction import ClickOnNewMessageAction
from script.extra.playwright.base_actions.FillAccountSearchForDmAction import FillAccountSearchForDmAction
from script.extra.playwright.base_actions.ClickOnFirstAccountSearchForDmAction import \
    ClickOnFirstAccountSearchForDmAction
from script.extra.playwright.base_actions.ClickOnChatAction import ClickOnChatAction
from script.extra.playwright.base_actions.ClickOnSendMessageAction import ClickOnSendMessageAction
from script.extra.playwright.base_actions.GoToAccountPageAction import GoToAccountPageAction
from script.extra.playwright.base_actions.GetThreadUrlAction import GetThreadUrlAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.models.Lead import Lead
from spintax import spin
from script.extra.adapters.SettingAdapter import SettingAdapter


class BrowserSendDmEvent:
    ig = None
    allowed_leads_count = None
    command = None
    lead = None
    error_indicators = None

    def __init__(self, ig):
        self.ig = ig
        self.error_indicators = ErrorIndicators(self.ig)

    def init(self):
        GoToThreadsAction(self.ig).start()
        TurnOnNotificationAction(self.ig).start()

        self.ig.account.add_cli("Starting DM process ...")

        self.allowed_leads_count = self.ig.account.current_chunk_dm
        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')

        while self.allowed_leads_count > 0:
            self.lead = Lead.get_leads()[0]
            self.lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

            self.send_dm()
            self.ig.pause(5000, 7000)
            self.allowed_leads_count -= 1

    def send_dm(self):

        try:
            self.ig.account.add_cli(f"Sending Dm to : {self.lead.username}")
            self.command = self.ig.account.create_command('dm follow up', 'processing', self.lead)
            self.before_message_fill_part()
            self.after_message_fill_part()

            self.ig.account.add_direct_url_id(self.lead.dm_text, self.lead, GetThreadUrlAction(self.ig).start())

            self.lead.change_state(self.ig.account, 'dm follow up', add_history=True, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")

            if self.command:
                self.command.update_cmd('state', 'fail')

            if str(e) == "Something went wrong":
                raise Exception(str(e))

    def before_message_fill_part(self):
        try:
            self.sending_direct_in_direct_page()

            if not self.ig.is_visible_by_text(f'{self.lead.username} · Instagram'):
                raise Exception('Could not send direct in direct page trying by search ...')

        except Exception as e:

            self.ig.account.add_cli(str(e))
            self.ig.page.keyboard.press("Escape")
            self.sending_direct_by_search()

    def sending_direct_in_direct_page(self):
        ClickOnNewMessageAction(self.ig).start()
        self.ig.pause(2000, 3000)

        FillAccountSearchForDmAction(self.ig).start(self.lead.username)
        self.ig.pause(3000, 5000)

        ClickOnFirstAccountSearchForDmAction(self.ig).start()
        self.ig.pause(1000, 3000)

        ClickOnChatAction(self.ig).start()
        self.ig.pause(3000, 4000)

    def sending_direct_by_search(self):
        GoToAccountPageAction(self.ig).start(self.lead.username)
        self.ig.pause(6000, 7000)

        ClickOnSendMessageAction(self.ig).start()
        self.ig.pause(3000, 4000)

    def after_message_fill_part(self):
        self.error_indicators.something_went_wrong_handler()
        self.error_indicators.not_every_one_can_message_this_account_handler(self.lead)
        self.error_indicators.send_more_messages_after_invite_accepted()

        # Fill the text box with DM text
        self.ig.page.get_by_label("Message", exact=True).fill(self.lead.dm_text)
        self.ig.pause(2000, 3500)

        try:
            self.ig.page.get_by_role("button", name="Turn On", exact=True).click(timeout=2000)
        except:
            pass

        try:
            self.ig.page.get_by_role("button", name="Send", exact=True).click()
        except:
            raise Exception("There's no Send button")

        self.ig.pause(3000, 5000)
