import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from time import sleep
from script.models.Account import Account
from script.models.TikTokLink import TikTokLink
from script.extra.base.BasePlaywright import BasePlaywright


class SaveTikTokLink:
    ig = None
    tik_tok_links = None
    link = None

    def __init__(self):
        account = Account.get_by_id(33)
        self.ig = BasePlaywright(account)
        self.ig.init()

        self.tik_tok_links = TikTokLink.select()
        self.ig.page.on('response', self.handle_response)

    def handle_response(self, response):
        if '/api/item/detail' not in response.url:
            return

        try:
            data = response.json()
        except Exception as e:
            print(str(e))
            # Body already gone → skip silently
            return

        stats = (
            data.get('itemInfo', {})
            .get('itemStruct', {})
            .get('statsV2', {})
        )

        if not stats:
            print('There is no stats')
            return

        print(f'🔥 Stats for {self.link.post_link}')
        print(json.dumps(stats, indent=2))

        self.link.comments = int(stats.get('commentCount', 0))
        self.link.likes = int(stats.get('diggCount', 0))
        self.link.shares = int(stats.get('shareCount', 0))
        self.link.saves = int(stats.get('collectCount', 0))
        self.link.play_counts = int(stats.get('playCount', 0))
        self.link.save()

    def go_to_page(self):
        max_retries = 5

        for attempt in range(max_retries):

            try:
                self.ig.page.goto(self.link.post_link, timeout=50000, wait_until="domcontentloaded")

                self.ig.pause(2000,3000)
                print('Reloading....')
                self.ig.page.reload(timeout=50000, wait_until="domcontentloaded")
                return True

            except Exception as e:
                print(f"Attempt {attempt + 1} failed for loading the page : {self.link.post_link}")

            self.ig.pause(3000, 4000)
        raise Exception(f"Failed to reach {self.link.post_link} after 5 attempts.")

    def main(self):

        for self.link in self.tik_tok_links:
            print(f'Going to page : {self.link.post_link}')
            self.go_to_page()
            print('After go to page Before time out...')
            self.ig.pause(3000, 4000)
            print('After go to page After time out...')

            if self.ig.is_visible_by_text("Video currently unavailable"):
                self.link.add_error('Video currently unavailable')
                continue

            self.ig.pause(2000, 3000)


SaveTikTokLink().main()