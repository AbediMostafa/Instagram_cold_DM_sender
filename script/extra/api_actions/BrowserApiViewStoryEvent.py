import random

from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import time
import re
import json
import requests
import traceback
from script.models.Order import get_next_order_for_account, Order
from script.extra.helper import go_to_page
from urllib.parse import parse_qs, unquote_plus


class BrowserApiViewStoryEvent(InstagramMiddleware):
    url = 'https://www.instagram.com/graphql/query'
    order = None
    listener = None

    def add_listener(self):
        """Attach temporary listener for Instagram suggestions"""

        def on_response(response):
            if '/graphql/query' in response.url:
                try:
                    payload_str = response.request.post_data
                    parsed = parse_qs(payload_str, keep_blank_values=True)

                    if 'fb_api_req_friendly_name' in parsed:
                        print('fb_api_req_friendly_name is in parsed')
                        print(parsed['fb_api_req_friendly_name'])
                        if parsed['fb_api_req_friendly_name']== 'PolarisStoriesV3SeenMutation':
                            variables = parsed['variables']
                            doc_id = parsed['doc_id']
                            print(variables)
                            print(doc_id)

                except Exception as e:
                    self.ig.account.add_cli(f"Error parsing response: {e}")

        # Save listener reference to remove it later
        self.listener = on_response
        self.ig.page.on("response", self.listener)

    def execute(self):
        self.send_main_request()
        # self.order = Order.get_by_id(13844)
        # self.order = get_next_order_for_account(self.ig.account)
        # print(f'order : {self.order.id}')
        # self.parse_link()

    def parse_link(self):
        link = self.order.target_link

        if 'stories' in link:
            go_to_page(self.ig, link, 'Story Page')
            self.add_listener()
            self.ig.pause(3000, 4000)
            self.click_on_view_story()
            self.ig.pause(3000, 4000)

    def click_on_view_story(self):
        if self.ig.is_visible_by_text(
                'will be able to see that you viewed their story') or self.ig.is_visible_by_text('View as'):
            self.ig.page.get_by_role("button", name=re.compile(r"View story", re.I)).click(timeout=3000)

    def send_main_request(self):
        view_seen_at = int(time.time()) - random.randint(30, 60)
        variables = json.dumps({
            "reelId": "72384674594",
            "reelMediaId": "3844905194874268042",
            "reelMediaOwnerId": "72384674594",
            "reelMediaTakenAt": 1772568437,
            "viewSeenAt": view_seen_at
        })

        self.ig.account.add_cli('Starting to view story via API ...')

        # Set body
        self.ig.graphql_data["payload"]["doc_id"] = 24372833149008516
        self.ig.graphql_data["payload"]["__crn"] = "comet.igweb.PolarisStoriesV3Route"
        self.ig.graphql_data["payload"]["fb_api_req_friendly_name"] = "PolarisStoriesV3SeenMutation"
        self.ig.graphql_data["payload"]["variables"] = variables

        # Set headers
        self.ig.graphql_data["headers"]["x-root-field-name"] = "xdt_api__v1__stories__reel__seen"
        self.ig.graphql_data["headers"]["x-fb-friendly-name"] = "PolarisStoriesV3SeenMutation"

        try:
            response = requests.post(self.url, headers=self.ig.graphql_data["headers"],
                                     data=self.ig.graphql_data["payload"])
        except Exception as e:
            self.ig.account.add_cli(f'Problem sending request to {self.url}: {e}')
            self.ig.account.add_log(traceback.format_exc())

        print(response.status_code)
        print(response.text)
        print(response.json())
