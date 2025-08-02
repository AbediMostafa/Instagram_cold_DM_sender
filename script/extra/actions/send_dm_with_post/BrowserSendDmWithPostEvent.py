import random

from script.extra.playwright.base_actions.ClickOnSendMessageAction import ClickOnSendMessageAction
from script.extra.playwright.base_actions.GetThreadUrlAction import GetThreadUrlAction
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.models.Lead import Lead
from script.models.Spintax import Spintax
from spintax import spin
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.DmPost import get_or_reset_dm_post_for_lead


class BrowserSendDmWithPostEvent:
    ig = None
    allowed_leads_count = None
    command = None
    lead = None
    error_indicators = None
    delivery_counter = 0
    message = spin(Spintax.get_value(times=0))

    zero_share_button_selector = 'span.x1rg5ohu button._abl-'
    first_share_button_selector = 'div.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xc5r6h4.xqeqjp1.x1phubyo.x13fuv20.x18b5jzi.x1q0q8m5.x1t7ytsu.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x14z9mp.xat24cr.x1lziwak.x2lwn1j.xeuugli.x1n2onr6.x16tdsg8.x1hl2dhg'
    second_share_button_selector = "span.x1rg5ohu button._abl-[type='button']"

    first_fill_username_input_selector = "input[name='queryBox']"

    first_message_input_selector = 'input[name="shareCommentText"]'
    second_message_input_selector = 'input[placeholder="Write a message..."]'

    message_sending_selector = 'svg[aria-label="igd message sending status icon" i]'
    message_failed_selector = 'svg[aria-label="Failed to send" i]'

    sending_icons = None
    failed_icons = None

    def __init__(self, ig):
        self.ig = ig
        self.error_indicators = ErrorIndicators(self.ig)

        # Get the account's category to send spintax with that category to the lead with the same category
        self.category_model = self.ig.account.category
        self.category = self.category_model.title if self.category_model else None

    def init(self):
        self.ig.account.add_cli("Starting DM with post process ...")
        self.ig.account.set_state('sending DM', 'app_state')

        leads = Lead.get_leads_for_dm(self.ig.account, random.randint(2, 4))
        # leads = Lead.get_leads_for_dm(self.ig.account, self.ig.account.current_chunk_dm)
        dm_post = get_or_reset_dm_post_for_lead(leads)

        self.send_dms(leads, dm_post)

        # for self.lead in leads:
        #     self.lead.dm_text = spin(Spintax.get_value(times=0))
        #     self.send_dm()
        #     self.ig.pause(5000, 7000)

    def send_dms(self, leads, dm_post):
        self.ig.page.goto(dm_post.title)
        self.ig.pause(4000, 6000)
        self.click_on_share_button()
        self.ig.pause(4000, 6000)
        self.fill_usernames(leads)
        self.ig.pause(2000, 3000)
        self.write_message()

        self.ig.pause(400000, 600000)
        # input[name='queryBox']

    def write_message(self):

        try:
            (self.ig.page
             .locator(self.first_message_input_selector)
             .fill(self.message, timeout=3000))

        except:

            self.ig.account.add_cli(f'Problem filling the message for the first locator input[name="shareCommentText"] trying second locator ...')

            (self.ig.page
             .locator(self.second_message_input_selector)
             .fill(self.message))

    def click_on_share_button(self):

        try:
            self.ig.page.locator(self.zero_share_button_selector).click(timeout=3000)
            self.ig.account.add_cli('Zero share locator clicked')

        except:
            self.ig.account.add_cli('Problem clicking on Zero share button trying first locator')

            try:
                self.ig.page.locator(self.first_share_button_selector).click(timeout=3000)

            except:
                self.ig.account.add_cli('Problem clicking on First share button trying second locator')
                self.ig.page.locator(self.second_share_button_selector).click(timeout=3000)

    def fill_usernames(self, leads):
        for lead in leads:
            (self.ig.page
             .locator(self.first_fill_username_input_selector)
             .press_sequentially(lead.username, delay=100, timeout=6000))
            self.ig.pause(5000, 7000)
            self.ig.page.click(f"text={lead.username}")
            self.ig.pause(2000, 3000)

    def send_dm(self):

        try:
            self.ig.account.add_cli(f"Sending Dm to : {self.lead.username}")
            self.command = self.ig.account.create_command('dm follow up', 'processing', self.lead,
                                                          category=self.category_model)
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
