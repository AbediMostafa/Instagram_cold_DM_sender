import random

from script.extra.playwright.base_actions.ClickOnSendMessageAction import ClickOnSendMessageAction
from script.extra.playwright.base_actions.GetThreadUrlAction import GetThreadUrlAction
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.models.Lead import Lead
from script.models.Spintax import Spintax
from spintax import spin
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.DmPost import get_dm_post_for_lead


class BrowserSendDmWithPostEvent:
    ig = None
    commands = []
    leads = []
    dm_post = None
    dm_text = None
    error_indicators = None
    delivery_counter = 0
    message = spin(Spintax.get_value(times=0))

    zero_share_button_selector = "div[role='button']:has(svg[aria-label='Share'])"
    # zero_share_button_selector = 'span.x1rg5ohu button._abl-'
    first_share_button_selector = "svg[aria-label='Share']"
    # first_share_button_selector = 'div.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xc5r6h4.xqeqjp1.x1phubyo.x13fuv20.x18b5jzi.x1q0q8m5.x1t7ytsu.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x14z9mp.xat24cr.x1lziwak.x2lwn1j.xeuugli.x1n2onr6.x16tdsg8.x1hl2dhg'
    second_share_button_selector = "div[role='button']:has(svg >> text=Share)"
    # second_share_button_selector = "span.x1rg5ohu button._abl-[type='button']"

    first_fill_username_input_selector = "input[name='queryBox']"

    first_message_input_selector = 'input[name="shareCommentText"]'
    second_message_input_selector = 'input[placeholder="Write a message..."]'

    message_sending_selector = 'svg[aria-label="igd message sending status icon" i]'
    message_failed_selector = 'svg[aria-label="Failed to send" i]'

    sending_icons = None
    failed_icons = None

    def __init__(self, ig):
        self.commands = []
        self.ig = ig
        self.error_indicators = ErrorIndicators(self.ig)
        self.dm_text = spin(Spintax.get_value(times=0))

        # Get the account's category to send spintax with that category to the lead with the same category
        self.category_model = self.ig.account.category
        self.category = self.category_model.title if self.category_model else None

    def init(self):
        self.ig.account.add_cli("Starting DM with post process ...")
        self.ig.account.set_state('sending DM', 'app_state')

        self.leads = Lead.get_leads_for_dm(self.ig.account, self.ig.account.current_chunk_dm)
        self.dm_post = get_dm_post_for_lead(priority=0)

        try:
            self.send_dms()
            self.update_all_success_statuses()

        except Exception as e:
            self.update_all_failed_statuses(e)

    def send_dms(self):
        self.ig.page.goto(self.dm_post.title)
        self.ig.pause(4000, 6000)
        self.click_on_share_button()
        self.ig.pause(4000, 6000)
        self.fill_usernames()

        self.ig.pause(2000, 3000)
        self.write_message()

        self.ig.pause(2000, 2500)
        self.click_on_send_separately()
        self.ig.pause(7000, 8000)

    def update_all_failed_statuses(self, e):
        self.ig.account.add_cli(f"Failed to send DM : {str(e)}")

        for command in self.commands:
            if command:
                command.update_cmd('state', 'fail')

    def update_all_success_statuses(self):
        for lead in self.leads:
            lead.change_state(self.ig.account, 'dm follow up', add_history=True, update_date=True)

        for command in self.commands:
            if command:
                command.update_cmd('state', 'success')

    def click_on_send_separately(self):
        import re

        try:
            self.ig.page.get_by_role("button", name=re.compile(r"send separately", re.I)).click(timeout=3000)

        except:
            self.ig.page.get_by_role("button", name=re.compile(r"send", re.I)).click(timeout=3000)

    def write_message(self):

        try:
            (self.ig.page
             .locator(self.first_message_input_selector)
             .fill(self.message, timeout=3000))

        except:

            self.ig.account.add_cli(
                f'Problem filling the message for the first locator input[name="shareCommentText"] trying second locator ...')

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
                self.ig.page.locator(self.first_share_button_selector).nth(1).click(timeout=3000)

            except:
                self.ig.account.add_cli('Problem clicking on First share button trying second locator')
                self.ig.page.locator(self.second_share_button_selector).click(timeout=3000)

    def fill_usernames(self):

        for lead in self.leads:
            self.ig.account.add_cli(f"Appending lead : {lead.username}")

            (self.ig.page
             .locator(self.first_fill_username_input_selector)
             .press_sequentially(lead.username, delay=100, timeout=6000))

            self.ig.pause(5000, 7000)

            if self.ig.is_visible_by_text('No results found'):
                self.ig.account.add_cli("No results found")
                self.ig.page.locator(self.first_fill_username_input_selector).fill('')
                continue

            try:
                self.ig.page.click(f"text={lead.username}", timeout=3000)
            except Exception as e:
                self.ig.account.add_cli("Problem clicking on username")
                continue

            self.ig.pause(2000, 3000)

            command = self.ig.account.create_command('dm follow up', 'processing', lead,
                                                     category=self.category_model)
            self.commands.append(command)

            self.ig.account.add_direct_url_id(self.dm_text, lead)
