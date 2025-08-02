import random

from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.LeadSource import get_lead_source
from script.models.Lead import Lead
from script.extra.parsers.FollowersParser import FollowersParser
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.base_actions.GetPostsAction import GetPostsAction
from script.extra.playwright.base_actions.ClickOnLikesAction import ClickOnLikesAction
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.extra.playwright.base_actions.ClickOnNextPostAction import ClickOnNextPostAction
from script.extra.playwright.base_actions.ClickOnFirstPostAction import ClickOnFirstPostAction
import re
from script.models.Hashtag import get_hashtag


class BrowserLeadGenerateByPostEngagementEvent:
    ig = None
    base = None
    parser = None
    category = None
    command = None
    hashtag_count = 1
    number_of_posts = 6

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
            self.command = self.ig.account.create_command('generate lead by post engagement', 'processing',
                                                          category=self.category_model)
            self.generate_lead()
            self.command.update_cmd('state', 'success')
        except Exception as e:
            self.ig.account.add_cli("Failed to generate lead by page engagement: " + str(e))
            if self.command:
                self.command.update_cmd('state', 'fail')

    def generate_lead(self):
        hashtags = get_hashtag(self.hashtag_count)

        for hashtag in hashtags:
            SearchForAction(self.ig).start(f'#{hashtag.title}')
            self.ig.pause(4000, 6000)

            self.ig.page.goto(f'https://www.instagram.com/explore/search/keyword/?q=%23{hashtag.title.lower()}')
            self.ig.pause(6000, 7000)
            self.get_leads()
            self.scroll()
            self.get_leads()

    def get_leads(self):
        ClickOnFirstPostAction(self.ig).start()
        self.ig.pause(5000, 6000)

        for _ in range(self.number_of_posts):
            try:
                ClickOnLikesAction(self.ig).start()
                self.ig.pause(5000, 6000)
                self.ig.page.keyboard.press('Escape')
                self.ig.pause(3000, 3500)
                ClickOnNextPostAction(self.ig).start()
                self.ig.pause(3000, 3500)
            except Exception as e:
                self.ig.account.add_cli(str(e))

        self.ig.page.keyboard.press('Escape')
        self.ig.pause(4000, 5000)

    def scroll(self):
        scroll_times = random.randint(5, 25)
        self.ig.account.add_cli(f'Scrolling {scroll_times} times')
        for _ in range(scroll_times):
            ScrollAction(self.ig).start(None, 500, 700, 3000, 4000)
