from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.LeadSource import get_lead_source
from script.models.Lead import Lead
from script.extra.parsers.FollowersParser import FollowersParser
from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
import re
import random
from script.extra.helper import go_to_page
from script.models.Location import get_next
from urllib.parse import parse_qs


class BrowserLeadGenerateByLocationEvent:
    ig = None
    command = None
    location_count = 1
    scroll_count = 3
    location = None
    listener = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        go_to_page(self.ig, "https://www.instagram.com/explore/locations/", 'Locations')
        self.ig.pause(7000, 8000)
        go_to_page(self.ig, "https://www.instagram.com/explore/locations/US/united-states/", 'Country')
        self.ig.pause(7000, 8000)
        self.ig.account.add_cli('Setting up listener ... ')
        self._setup_listener()
        self.ig.pause(2000, 2500)

        for i in range(self.location_count):
            try:
                self.location = get_next()
                self.ig.account.add_cli(f'Selected location {self.location.name}')

                url = f"https://www.instagram.com/explore/locations/{self.location.location_id}/"
                go_to_page(self.ig, url, "Location")
                self.ig.pause(7000, 8000)
                self._scroll()

            except Exception as e:
                self.ig.account.add_cli("Failed to generate lead by Location : " + str(e))

        self.ig.page.remove_listener("response", self.listener)
        self.listener = None

    def _setup_listener(self):
        """Listen for profile response"""

        def on_response(response):
            if 'graphql/query' not in response.url:
                return

            post_data = response.request.post_data

            if not post_data:
                self.ig.account.add_cli("There's no Post data ... ")
                return

            parsed = parse_qs(post_data, keep_blank_values=True)
            fb_api_name = parsed.get('fb_api_req_friendly_name', [''])[0]

            if 'PolarisLocationPageTabContentQuery_connection' not in fb_api_name:
                return

            response = response.json()
            data = response.get("data", {})
            xdt = data.get("xdt_location_get_web_info_tab", {})
            edges = xdt.get("edges", {})

            self.ig.account.add_cli(f'Found {len(edges)} Nodes ...')

            # Get country from the location's city
            country = None
            if self.location and self.location.city:
                country = self.location.city.country

            for edge in edges:
                node = edge.get("node", {})
                username = node.get("user").get("username")

                try:
                    Lead.get_or_create(
                        username=username,
                        defaults={'country': country}
                    )
                except Exception as e:
                    pass

        self.listener = on_response
        self.ig.page.on('response', on_response)

    def _scroll(self):

        for i in range(self.scroll_count):
            self.ig.page.mouse.wheel(0, random.randint(600, 750))
            self.ig.pause(2000, 4000)