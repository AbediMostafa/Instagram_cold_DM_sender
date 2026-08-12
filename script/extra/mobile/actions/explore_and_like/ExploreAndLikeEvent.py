import time
import random

from script.models.Setting import Setting
from script.extra.mobile.base.BaseMobileEvent import BaseMobileEvent


class ExploreAndLikeEvent(BaseMobileEvent):
    """
    Browse Explore once: open a single item from the grid, then swipe through
    the following posts, liking each with a fixed probability (default 20%).

    Swiping (rather than opening and closing one tile at a time) is both far
    cheaper and much closer to real use. Tapping back to the grid for every
    post costs an extra tap + back per item on an API limited to one request a
    second, and it looks nothing like how a person browses.

    Liking is done with a double-tap on the media rather than by hunting for
    a like button. Explore mixes feed posts and reels whose like controls have
    different ids and positions, while the double-tap gesture works on all of
    them, costs one API call instead of a dump plus a tap, and is what a person
    actually does. Instagram's double-tap only ever likes — it never unlikes —
    so it's safe to repeat.
    """

    EXPLORE_TAB = {'rid': 'search_tab'}

    # Where to tap in the Explore grid to open the first item. Tiles carry no
    # stable resource-id, so a point inside the grid area is the usual approach.
    GRID_TAP = (540, 1000)

    # Where to double-tap to like: the middle of the media area, clear of the
    # top action bar and the bottom caption/tab bar.
    MEDIA_CENTER = (540, 900)

    # Only used to confirm an item is actually open (see _open_first_item);
    # liking itself doesn't depend on finding a button.
    OPEN_ITEM_MARKERS = [
        {'rid': 'like_button'},
        {'rid': 'row_feed_button_like'},
        {'rid': 'clips_viewer_view_pager'},
        {'rid': 'clips_media_component'},
        {'rid': 'media_group'},
    ]

    def init(self):
        if not self._open_explore():
            self.log('could not open Explore; skipping')
            return

        min_posts = int(Setting.get_value('mobile_explore_min_posts', 7))
        max_posts = int(Setting.get_value('mobile_explore_max_posts', 12))
        like_chance = float(Setting.get_value('mobile_explore_like_chance', 0.2))
        min_dwell = float(Setting.get_value('mobile_explore_min_dwell', 8))
        max_dwell = float(Setting.get_value('mobile_explore_max_dwell', 20))
        if min_dwell > max_dwell:
            min_dwell, max_dwell = max_dwell, min_dwell

        # Guard against a mis-set range so randint never throws.
        if min_posts > max_posts:
            min_posts, max_posts = max_posts, min_posts
        posts_to_view = random.randint(min_posts, max_posts)

        if not self._open_first_item():
            self.log('could not open an item from the Explore grid')
            return

        self.log(f'browsing Explore, viewing {posts_to_view} posts '
                 f'(like chance {int(like_chance * 100)}%)')

        liked = 0
        for index in range(posts_to_view):
            # Watch the post for a while before deciding, the way a person
            # would — this is also what makes the session look like real use
            # rather than a scripted crawl.
            dwell = random.uniform(min_dwell, max_dwell)
            self.log(f'post {index + 1}/{posts_to_view}: watching {dwell:.0f}s')
            time.sleep(dwell)

            if random.random() < like_chance and self._like_current():
                liked += 1
                self.log(f'post {index + 1}/{posts_to_view}: liked (total {liked})')

            # Swipe to the next post, except after the last one.
            if index < posts_to_view - 1:
                self._swipe_to_next()

        self.log(f'Explore done ({posts_to_view} viewed, {liked} liked)')

    # ── navigation ──────────────────────────────────────────────────────────
    def _open_explore(self):
        d = self.device
        if d.foreground_package() != d.INSTAGRAM_PKG:
            self.log('Instagram not in foreground; starting app')
            d.start_app()

        self.log('opening Explore tab')
        hit = d.wait_for(self.EXPLORE_TAB, timeout=15)
        if not hit:
            return False
        d.tap(hit[0], hit[1])
        time.sleep(3)
        return True

    def _open_first_item(self):
        """
        Open one tile from the grid. Success is confirmed by finding a like
        control (or any clips/feed container) rather than trusting the tap,
        since a mistimed tap can land on a gap and leave us on the grid.
        """
        d = self.device
        self.log('opening first item from Explore grid')
        d.tap(*self.GRID_TAP)
        time.sleep(3)

        xml = d.dump_xml()
        # A like control or a media container means an item is open; if the tap
        # landed on a gap we're still on the grid.
        return any(d.find(xml, marker) for marker in self.OPEN_ITEM_MARKERS)

    def _swipe_to_next(self):
        # A full-height swipe advances to the next item in both the reels
        # viewer and the post-by-post Explore feed.
        self.log('swiping to next post')
        self.device.swipe_up(distance=random.randint(900, 1200), duration_ms=250)
        time.sleep(random.uniform(1.0, 2.0))

    # ── liking ──────────────────────────────────────────────────────────────
    def _like_current(self):
        """
        Like the item on screen with a double-tap. No dump is needed, so this
        is one API call rather than three, and it works on posts and reels
        alike.
        """
        self.device.double_tap(*self.MEDIA_CENTER)
        time.sleep(random.uniform(0.8, 1.6))
        return True