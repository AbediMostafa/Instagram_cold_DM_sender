from datetime import datetime
import random
from script.models.AccountSpec import AccountSpec
from script.extra.helper import go_to_page
from script.extra.helper import tehran_now


class BrowserReelsAverageExtractorEvent:
    MAX_SCROLLS = 100
    MAX_IDLE_SCROLLS = 3

    def __init__(self, ig):
        self.ig = ig

        self.reel_ids = set()
        self.play_counts = []

        self.media_count = None  # from user.media_count
        self.scroll_count = 0
        self.idle_scrolls = 0
        self.last_count = 0

        self.ig.page.on('response', self._handle_response)

    def _handle_response(self, response):
        if 'graphql/query' not in response.url:
            return

        try:
            data = response.json().get('data', {})
        except:
            return

        if not data:
            return

        user = data.get('user')

        if user and self.media_count is None:
            self.media_count = user.get('media_count')
            self.ig.account.add_cli(
                f'Media count detected: {self.media_count}'
            )

        reels = data.get('xdt_api__v1__clips__user__connection_v2')

        if not reels:
            return

        for edge in reels.get('edges', []):
            media = edge.get('node', {}).get('media')
            if not media:
                continue

            media_id = media.get('pk')
            if not media_id or media_id in self.reel_ids:
                continue

            self.reel_ids.add(media_id)

            play_count = media.get('play_count')
            self.play_counts.append(play_count)

    def scroll(self):
        while self.should_scroll() and self.scroll_count < self.MAX_SCROLLS:
            self.ig.page.mouse.wheel(0, random.randint(1200, 1800))
            self.ig.pause(1200, 2000)
            self.scroll_count += 1

        self.ig.page.remove_listener('response', self._handle_response)

    def should_scroll(self):
        if self.media_count is None:
            return True

        if len(self.play_counts) < self.media_count:
            self.ig.account.add_cli(f'{len(self.play_counts)} {self.media_count}')

            if len(self.play_counts) == self.last_count:
                self.idle_scrolls += 1
            else:
                self.idle_scrolls = 0
                self.last_count = len(self.play_counts)

            if self.idle_scrolls >= self.MAX_IDLE_SCROLLS:
                self.ig.account.add_cli('No more reels detected, stopping scroll')
                return False

            self.ig.account.add_cli('should scroll more ...')
            return True

        return False

    def init(self):
        go_to_page(self.ig, f'https://www.instagram.com/{self.ig.account.username}/reels', 'Account')
        self.ig.pause(2000, 3000)
        self.scroll()

        if not self.play_counts:
            self.ig.account.add_cli("There's no play counts")

            return

        reels_count = len(self.play_counts)
        total_views = sum(self.play_counts)

        self.ig.account.add_cli(
            f'Reels stats saved | avg: {int(total_views / reels_count)} | count: {reels_count}'
        )

        # Try to get existing spec
        spec, created = AccountSpec.get_or_create(account=self.ig.account)

        # Update with new data
        spec.reels_count = reels_count
        spec.avg_reel_views = int(total_views / reels_count)
        spec.min_reel_views = min(self.play_counts)
        spec.max_reel_views = max(self.play_counts)
        spec.total_reel_views = total_views
        spec.last_reels_scan_at = tehran_now()
        spec.save()
