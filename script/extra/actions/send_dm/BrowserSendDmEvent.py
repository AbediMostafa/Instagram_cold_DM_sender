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
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.models.Lead import Lead
from script.models.Spintax import Spintax
from spintax import spin
from script.extra.adapters.SettingAdapter import SettingAdapter


class BrowserSendDmEvent:
    ig = None
    allowed_leads_count = None
    command = None
    lead = None
    error_indicators = None
    delivery_counter = 0

    message_sending_selector = 'svg[aria-label="igd message sending status icon" i]'
    message_failed_selector = 'svg[aria-label="Failed to send" i]'

    sending_icons = None
    failed_icons = None

    def __init__(self, ig):
        self.ig = ig
        self.error_indicators = ErrorIndicators(self.ig)

        # Get the account's category to send spintax with that category to the lead with the same category
        # self.category_model = self.ig.account.category
        # self.category = self.category_model.title if self.category_model else None

    def init(self):
        self.ig.account.add_cli("Starting DM process ...")
        self.ig.account.set_state('sending DM', 'app_state')
        self.ig.account.add_cli(f"Current chunck dm : {2}")
        # self.ig.account.add_cli(f"Current chunck dm : {self.ig.account.current_chunk_dm}")

        leads = Lead.get_leads_for_dm(self.ig.account, 2)
        # leads = Lead.get_leads_for_dm(self.ig.account, self.ig.account.current_chunk_dm)

        for self.lead in leads:
            self.lead.dm_text = spin(Spintax.get_value(times=0))
            self.send_dm()
            self.ig.pause(5000, 7000)

    def send_dm(self):

        try:
            self.ig.account.add_cli(f"Sending Dm to : {self.lead.username}")
            self.command = self.ig.account.create_command('dm follow up', 'processing', self.lead)
            self.before_message_fill_part()
            self.after_message_fill_part()
            self.check_message_delivery()

            url_id = GetThreadUrlAction(self.ig).start()
            self.ig.account.add_direct_url_id(self.lead.dm_text, self.lead, url_id)

            self.lead.change_state(self.ig.account, 'dm follow up', add_history=True, update_date=True)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")

            if self.command:
                self.command.update_cmd('state', 'fail')

            if str(e) == "Something went wrong":
                raise Exception(str(e))

    def before_message_fill_part(self):
        DirectlyGoToAccountPageAction(self.ig).start(self.lead.username)
        self.ig.pause(6000, 7000)

        ClickOnSendMessageAction(self.ig).start()
        self.ig.pause(4000, 5000)

        try:
            self.ig.page.get_by_role("button", name="Expand").click(timeout=3000)
        except:
            pass

    def after_message_fill_part(self):
        self.error_indicators.something_went_wrong_handler()
        self.error_indicators.not_every_one_can_message_this_account_handler(self.lead)
        self.error_indicators.send_more_messages_after_invite_accepted()

        try:
            self.ig.page.get_by_role("button", name="Turn On", exact=True).click(timeout=2000)
        except:
            pass
        # Fill the text box with DM text
        self.ig.page.get_by_label("Message", exact=True).fill(self.lead.dm_text)
        self.ig.pause(2000, 3500)



        try:
            self.ig.page.get_by_role("button", name="Send", exact=True).click()
        except:
            raise Exception("There's no Send button")

        self.ig.pause(3000, 5000)

    def check_message_delivery(self):

        self.sending_icons = self.ig.page.query_selector_all(self.message_sending_selector)

        while self.sending_icons:
            self.delivery_counter += 1

            self.ig.account.add_cli('Sending message ...')
            self.sending_icons = self.ig.page.query_selector_all(self.message_sending_selector)
            self.ig.pause(1000, 1800)

            if self.delivery_counter >= 7:
                raise Exception("Failed to send message --> Stuck in sending message state")

        self.ig.pause(2000, 2500)
        self.failed_icons = self.ig.page.query_selector_all(self.message_failed_selector)

        if self.failed_icons:
            raise Exception("Failed to send message")
