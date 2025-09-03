from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
import random


class BrowserGotoExploreEvent(InstagramMiddleware):

    def execute(self):
        self.go_to_explore()
        self.ig.suspect_automate_behavior_handler()

        self.base.scroll(times=random.randint(3, 5))

    def go_to_explore(self):
        self.ig.account.add_cli('Going to explore page ...')
        retries = 1
        for attempt in range(retries):
            try:
                try:
                    self.ig.page.get_by_role("link", name="Explore Explore").click(timeout=3000)
                except:
                    go_to_page(self.ig, "https://www.instagram.com/explore/", "Explore")

                break
            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                sleep(2)
        self.ig.pause(4000, 6000)
        return self
