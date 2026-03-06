from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.LeadSource import get_lead_source
from script.models.Lead import Lead
from script.extra.parsers.FollowersParser import FollowersParser
from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
import re
from script.extra.helper import go_to_page


class BrowserGetRequestsPayloadAndHeaderEvent:
    ig = None

    def __init__(self, ig):
        self.ig = ig
        self.ig.page.on("response", lambda response: self.handle_response(response))

    def handle_response(self, response):
        pattern = re.compile(r'/api/v1/friendships/\d+/followers')

        if pattern.search(response.url):
            json_response = response.json()
            self.process_response(json_response)

    def process_response(self, json):
        self.parser = FollowersParser(json, self.ig.account)

        try:
            self.parser.parse()
        except Exception as e:
            self.ig.account.add_cli(str(e))

        self.ig.account.add_cli(f'Found {len(self.parser.usernames)} leads...')

        self.insert_leads()


    def init(self, lead_source_count):
        lead_sources = get_lead_source(lead_source_count, self.ig.account.category)

        try:
            self.command = self.ig.account.create_command('generate lead by followers', 'processing',
                                                          category=self.category_model)
            self.generate_lead(lead_sources)
            self.command.update_cmd('state', 'success')
        except Exception as e:
            self.ig.account.add_cli("Failed to generate lead by followers: " + str(e))
            if self.command:
                self.command.update_cmd('state', 'fail')

    def generate_lead(self, lead_sources):
        for lead_source in lead_sources:
            self.category = lead_source.category
            go_to_page(self.ig, f'https://www.instagram.com/{lead_source.title}', "Lead source")
            self.ig.pause(4000, 6000)

            if self.ig.is_visible_by_text('No results') or self.ig.is_visible_by_text("We couldn't find anything"):
                self.ig.account.add_cli("We couldn't find anything for that search.")
                continue

            self.ig.page.keyboard.press('Escape')

            self.click_on_followers()
            self.ig.pause(6000, 7000)
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(2000, 3000)

    def click_on_followers(self):

        try:
            self.ig.page.get_by_role("link", has_text="followers").click(timeout=4000)

        except Exception as e:
            self.ig.account.add_cli('Problem clicking on followers for the first time ... trying second method')
            self.ig.page.locator("a:has-text('followers')").click(timeout=4000)
