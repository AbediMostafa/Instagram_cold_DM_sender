from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Hashtag import get_hashtag
from script.models.Lead import Lead
from script.extra.parsers.GridPostParser import GridPostParser
from script.extra.playwright.base_actions.SearchForAction import SearchForAction


class BrowserLeadGenerateThroughApiEvent:
    ig = None
    base = None
    parser = None
    category = None

    def __init__(self, ig):
        self.ig = ig
        self.base = BrowserBaseEvent(self.ig)
        self.ig.page.on("response", lambda response: self.handle_response(response))
        self.search_for = SearchForAction(self.ig)

    def handle_response(self, response):
        if '/api/v1/fbsearch/web/top_serp/' in response.url:
            json_response = response.json()
            self.process_response(json_response)

    def process_response(self, json):
        self.parser = GridPostParser(json, self.ig.account)

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
                self.ig.account.add_cli(f"Failed to insert lead {username}: {str(e)}")

    def init(self, hashtag_count):
        hashtags = get_hashtag(hashtag_count, self.ig.account.category)

        for hashtag in hashtags:
            self.category = hashtag.category
            self.search_for.start(f'#{hashtag.title}')
            self.ig.pause(4000, 6000)

            if self.ig.is_visible_by_text('No results found'):
                self.ig.account.add_cli(f'No leads found for {hashtag.title}')
                hashtag.delete_instance()
                continue

            try:
                self.ig.page.locator(
                    "div.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.xh8yej3.xocp1fn a").first.click(timeout=4000)

            except Exception as e:
                self.ig.account.add_cli(f'Problem clicking on first a hashtag {str(e)}')
                self.ig.page.locator(f'a[href="/explore/tags/{hashtag.title.lower()}/"]').first.click(timeout=3000)

            self.ig.pause(4000, 6000)

            if self.ig.is_visible_by_text('No results') or self.ig.is_visible_by_text("We couldn't find anything"):
                self.ig.account.add_cli("We couldn't find anything for that search.")
                continue

            self.ig.page.keyboard.press('Escape')

            self.base.scroll(15)
