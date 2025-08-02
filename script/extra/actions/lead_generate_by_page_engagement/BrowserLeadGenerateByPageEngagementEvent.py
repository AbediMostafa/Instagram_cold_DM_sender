import random

from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.LeadSource import get_lead_source
from script.models.Lead import Lead
from script.extra.parsers.FollowersParser import FollowersParser
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.base_actions.GetPostsAction import GetPostsAction
from script.extra.playwright.base_actions.ClickOnLikesAction import ClickOnLikesAction
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
import re


class BrowserLeadGenerateByPageEngagementEvent:
    ig = None
    base = None
    parser = None
    category = None
    command = None
    counter = 0
    lead_source_count = 1
    post_count = 4
    lead_source = None

    def __init__(self, ig):
        self.ig = ig
        self.category_model = self.ig.account.category
        self.ig.page.on("response", lambda response: self.handle_response(response))

    def handle_response(self, response):
        pattern = re.compile(r'/api/v1/media/\d+/likers/')

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

    def init(self):
        self.ig.page.goto('https://www.instagram.com')
        self.ig.pause(4000, 5000)

        try:
            self.command = self.ig.account.create_command('generate lead by page engagement', 'processing',
                                                          category=self.category_model)
            self.generate_lead()
            self.command.update_cmd('state', 'success')
        except Exception as e:
            self.ig.account.add_cli("Failed to generate lead by page engagement: " + str(e))
            if self.command:
                self.command.update_cmd('state', 'fail')

    def generate_lead(self):
        lead_sources = get_lead_source(self.lead_source_count, self.ig.account.category)

        for self.lead_source in lead_sources:
            DirectlyGoToAccountPageAction(self.ig).start(self.lead_source.title)
            self.ig.pause(5000, 7000)

            # First get liker of first n posts
            self.get_leads()
            self.scroll()

            # Then scroll and get liker of n posts
            self.get_leads()

    def get_leads(self):
        posts, total_posts = self.get_posts()

        if total_posts == 0:
            self.ig.account.add_cli(f'No posts found for {self.lead_source.title}')
            return False

        for _ in range(min(self.post_count, total_posts)):
            post = posts.nth(_)

            post.locator('a').first.click(timeout=3000)

            self.ig.pause(3000, 4000)
            ClickOnLikesAction(self.ig).start()
            self.ig.pause(5000, 6000)

            # First for likes modal
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(2000, 3000)

            # Second for post modal
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(2000, 3000)

    def scroll(self):
        scroll_times = random.randint(1, 30)

        self.ig.account.add_cli(f'Scrolling {scroll_times} times')
        for _ in range(scroll_times):
            ScrollAction(self.ig).start(None, 500, 700, 3000, 4000)

    def get_posts(self):
        posts = GetPostsAction(self.ig).start()

        return posts, posts.count()
