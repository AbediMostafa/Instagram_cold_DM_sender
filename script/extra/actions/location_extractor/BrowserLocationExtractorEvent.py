import traceback
from script.extra.helper import go_to_page
from script.models.City import get_next
from script.models.Location import Location
import random


class BrowserLocationExtractorEvent:
    number_of_locations_to_extract = 10
    command = None
    account_to_check = None
    city = None
    listener = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        go_to_page(self.ig, "https://www.instagram.com/explore/locations/", 'Locations')
        self.ig.pause(7000, 8000)
        go_to_page(self.ig, "https://www.instagram.com/explore/locations/IL/israel/", 'Country')
        self.ig.pause(7000, 8000)
        self.ig.account.add_cli('Setting up listener ... ')
        self._setup_listener()
        self.ig.pause(7000, 8000)

        for i in range(3):
            self.city = get_next()
            go_to_page(self.ig, f"https://www.instagram.com/explore/locations/{self.city.city_id}/{self.city.slug}/",
                       'Location')
            self.ig.pause(7000, 8000)

            for i in range(5):
                self._scroll()
                self.ig.page.get_by_role("link", name="See more").click()
                self.ig.pause(5000, 6000)

        self.ig.page.remove_listener("response", self.listener)
        self.listener = None

    def _setup_listener(self):
        """Listen for profile response"""

        def on_response(response):
            if 'locations/city/directory' not in response.url:
                return

            response = response.json()
            locations = response.get("location_list", {})
            self.ig.account.add_cli(f'Found {len(locations)} locations...')

            for location in locations:
                Location.get_or_create(
                    location_id=location['id'],
                    name=location['name'],
                    slug=location['slug'],
                    city=self.city
                )

        self.listener = on_response
        self.ig.page.on('response', on_response)

    def _scroll(self):

        for i in range(2):
            self.ig.page.mouse.wheel(0, random.randint(450, 650))
            self.ig.pause(2000, 4000)
