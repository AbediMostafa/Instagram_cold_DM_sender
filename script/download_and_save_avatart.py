import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from time import sleep
from script.models.Account import Account
from script.models.TikTokLink import TikTokLink
from script.extra.base.BasePlaywright import BasePlaywright
from script.extra.helper import tehran_now


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
            saved_images = self.download_images(data)
            print(saved_images)
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
        self.link.updated_at = tehran_now()
        self.link.save()

    def go_to_page(self):
        max_retries = 5

        for attempt in range(max_retries):

            try:
                self.ig.page.goto(self.link.post_link, timeout=50000, wait_until="domcontentloaded")

                self.ig.pause(2000, 3000)
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
            self.ig.pause(3000, 4000)

            if self.ig.is_visible_by_text("Video currently unavailable"):
                self.link.add_error('Video currently unavailable')
                continue

            self.ig.pause(2000, 3000)

    def download_images(self, data):
        import requests
        from pathlib import Path

        images = (
            data.get('itemInfo', {})
            .get('itemStruct', {})
            .get('imagePost', {})
            .get('images', [])
        )

        if not images:
            return []

        project_root = Path(__file__).resolve().parents[1]
        base_path = project_root / "backend" / "storage" / "app" / "public" / "tiktok" / str(self.link.id)

        print(f'Base Path : {base_path}')
        base_path.mkdir(parents=True, exist_ok=True)

        saved_images = []

        for index, img in enumerate(images):
            try:
                url = img.get('imageURL', {}).get('urlList', [])[0]
                if not url:
                    continue

                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    file_path = base_path / f"{index + 1}.jpg"
                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    saved_images.append(f"tiktok/{self.link.id}/{index + 1}.jpg")

            except Exception as e:
                print(f"Error downloading image: {str(e)}")

        return saved_images


SaveTikTokLink().main()
