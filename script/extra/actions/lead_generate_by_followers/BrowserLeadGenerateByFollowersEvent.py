from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.LeadSource import get_lead_source
from script.models.Lead import Lead
from script.extra.parsers.FollowersParser import FollowersParser
from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
import re
from script.extra.helper import go_to_page


class BrowserLeadGenerateByFollowersEvent:
    ig = None
    base = None
    parser = None
    category = None
    command = None
    scroll_times = 20
    # scroll_container = 'div.xyi19xy.x1ccrb07.xtf3nb5.x1pc53ja.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6'
    # scroll_container = 'div.x7r02ix.x1bphaa0.x18nydb4.xcm95gh.x1vsb9q8.xb88tzc.xw2csxc.x1odjw0f.x5fp0pe'
    scroll_container = 'div.x6nl9eh.x1a5l9x9.x7vuprf.x1mg3h75.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6'

    def __init__(self, ig):
        self.ig = ig
        self.category_model = self.ig.account.category
        self.base = BrowserBaseEvent(self.ig)
        self.ig.page.on("response", lambda response: self.handle_response(response))
        self.search_for = SearchForAction(self.ig)
        self.scroll = ScrollAction(self.ig).start

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

    def insert_leads(self):
        for username in self.parser.usernames:
            try:
                Lead.get_or_create(username=username, category=self.category)
            except Exception as e:
               pass

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
            self.search_for.start(lead_source.title)
            self.ig.pause(4000, 6000)

            if self.ig.is_visible_by_text('No results found'):
                self.ig.account.add_cli(f'No lead source found for {lead_source.title}')
                continue

            try:
                self.ig.page.locator(
                    "div.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.xh8yej3.xocp1fn a").first.click(timeout=4000)

            except Exception as e:
                self.ig.account.add_cli(f'Problem clicking on first a lead_source {str(e)}')
                go_to_page(self.ig, f'https://www.instagram.com/{lead_source.title}', "Lead source")


            self.ig.pause(4000, 6000)

            if self.ig.is_visible_by_text('No results') or self.ig.is_visible_by_text("We couldn't find anything"):
                self.ig.account.add_cli("We couldn't find anything for that search.")
                continue

            self.ig.page.keyboard.press('Escape')

            self.click_on_followers()

            for _ in range(self.scroll_times):
                self.scroll(self.scroll_container, 400, 600, 5000, 7000)

            self.ig.pause(2000, 3000)
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(2000, 3000)

    def click_on_followers(self):

        try:
            self.ig.page.get_by_role("link", has_text="followers").click(timeout=4000)

        except Exception as e:
            self.ig.account.add_cli('Problem clicking on followers for the first time ... trying second method')
            self.ig.page.locator("a:has-text('followers')").click(timeout=4000)
