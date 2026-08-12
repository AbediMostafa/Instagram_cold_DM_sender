import re
import time
import random
import xml.etree.ElementTree as ET

from script.extra.exceptions import RetryableError
from script.extra.mobile.base.LinkParser import LinkParser


class ShareGroupsUnavailable(RetryableError):
    """
    This account could not surface enough share_group_* chats to fulfil the
    requested send. Treated as retryable: the order/action goes back to the
    pool for another account whose groups are intact.
    """


class ShareMechanics:
    """
    The share UI flow shared by SharePrepareEvent and ShareEvent: open the
    target (post / reel / story) by URL, validate it with the same error
    classification the web prepare handlers use, then tick N share groups in
    the share sheet and fire ONE send.

    All selectors below come from real device dumps (phase-8 dump sessions
    01-14, SM-X826B, IG share sheet = the direct_private_share_* component,
    identical for posts and stories):

      - plane button:   post  -> row_feed_button_share  (desc 'Send post';
                                 clickable=false but bounds are tappable)
                        reel  -> direct_share_button    (desc 'Share')
                        story -> toolbar_reshare_button (desc 'Share')
      - story interstitial 'View as X?' -> story_interstitial_cta_button
      - sheet grid tile: direct_share_sheet_grid_view_pog with content-desc
        '<name> Chat selected' / '<name> Chat not selected' — the selection
        state itself lives in the desc, so every tap is verifiable.
      - search: search_edit_text; result rows: user_row_background containing
        row_user_primary_name + recipient_toggle (checkable, checked attr).
      - send: direct_send_button_multi_select ('Send separately') — one tap
        sends to every ticked chat separately. NEVER the sibling
        direct_send_to_group_button_vertical ('Create group chat').

    Strategy (confirmed on device): grid-first. Tiles toggle in place and the
    grid survives ticks, while ticking a search row drops the sheet back to
    the grid — so search is only the fallback for groups the grid never
    surfaced, and after typing we must WAIT for the result list to load.
    """

    GROUP_PREFIX = 'share_group_'

    # Groups are named share_group_1 .. share_group_20. Bounds the search
    # fallback's numeric range; the real per-send cap is groups_needed.
    MAX_GROUPS = 20

    # Bottom-sheet drag handle (the little bar above the search box, ~x=540
    # y=703 in dumps). Dragging it to the top expands the sheet full-screen so
    # the grid stops collapsing to the recent row after a few selections and
    # every group becomes scroll-reachable (confirmed on device: all 20).
    EXPAND_SWIPE = (540, 703, 540, 150, 400)     # x1,y1,x2,y2,duration_ms
    # Scroll gestures live INSIDE the expanded recycler (y 306..1410). Long
    # throws well clear of both edges so the list actually pages instead of
    # nudging, and slow enough (500ms) to register as a scroll not a fling.
    SCROLL_DOWN = (540, 1250, 540, 500, 500)     # page down inside expanded list
    SCROLL_UP = (540, 500, 540, 1250, 500)       # page up / collapse

    # Sheet selectors
    SHEET_RECYCLER = {'rid': 'direct_private_share_recipients_recycler_view'}
    SEARCH_FIELD = {'rid': 'search_edit_text'}
    SEARCH_CLEAR = {'rid': 'action_button'}
    SEND_BUTTON = {'rid': 'direct_send_button_multi_select'}
    GRID_TILE_RID = 'direct_share_sheet_grid_view_pog'
    ROW_CONTAINER_RID = 'user_row_background'
    ROW_NAME_RID = 'row_user_primary_name'
    ROW_TOGGLE_RID = 'recipient_toggle'

    # Target-page selectors. Reels are opened via /p/ so they render in the
    # post viewer — both use the post share button. The reel-native button is
    # kept as a fallback in case a build ever lands a reel in the clips viewer.
    SHARE_BUTTONS = {
        LinkParser.TYPE_POST: [{'rid': 'row_feed_button_share'},
                               {'desc': 'Send post'}],
        LinkParser.TYPE_REEL: [{'rid': 'row_feed_button_share'},
                               {'desc': 'Send post'},
                               {'rid': 'direct_share_button'}],
        LinkParser.TYPE_STORY: [{'rid': 'toolbar_reshare_button'}],
    }
    STORY_INTERSTITIAL = {'rid': 'story_interstitial_cta_button'}
    # Fixed centre of the 'View story' button for blind-tapping (dumps put it
    # at ~507,1179 and ~554,1295; the button is large, so this centre hits it).
    VIEW_STORY_TAP = (530, 1240)
    # Fixed centre of the story viewer's reshare (Share) button — tapped blind
    # right after entering the viewer so the share sheet opens before the
    # story auto-advances (toolbar_reshare_button at 996,1680 in dumps).
    STORY_RESHARE_TAP = (996, 1680)
    PROFILE_HEADER = {'rid': 'row_profile_header'}
    STORY_VIEWER = {'rid': 'reel_view_group'}

    # Page texts ported from SavePostPrepareHandler / StoryPrepareHandler.
    # On mobile these are matched against the app's dumped XML instead of the
    # browser URL/body.
    PERMANENT_TEXTS = [
        'This account is private',
        'This profile is private',
        "Post isn't available",
        'The link may be broken',
        'profile may have been removed',
        "Sorry, this page isn't available",
        'Page is not available',
        "This page isn't available",
        'Story is unavailable',
        'This story is unavailable',
        'no active story',
    ]
    RETRYABLE_TEXTS = [
        "There's an issue and the page could not be loaded",
        'Something went wrong',
        'Try again later',
        "Couldn't load",
    ]

    MAX_GRID_ROUNDS = 30
    MAX_SEARCH_ATTEMPTS = 12
    BOUNDS_RE = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')

    def __init__(self, device):
        self.device = device
        self.account = device.account
        self._sheet_prelaunched = False   # story path opens the sheet early

    def log(self, msg):
        if self.account:
            self.account.add_cli(f'[ShareMechanics] {msg}')
        else:
            print(f'[ShareMechanics] {msg}')

    def detail(self, msg):
        """Fine-grained UI line, prefixed to stand out from step logs."""
        if self.account:
            self.account.add_cli(f'[ShareMechanics]   . {msg}')
        else:
            print(f'[ShareMechanics]   . {msg}')

    # ── opening & validating the target ─────────────────────────────────────
    def build_target_url(self, parsed):
        """
        Canonical app URL for a LinkParser result (or action_data dict).

        Posts AND reels are opened via /p/{code}/ on purpose: Instagram serves
        a reel opened through the /p/ path in the feed (post) viewer, so the
        share flow only ever deals with ONE UI — the post's share button
        (row_feed_button_share) — instead of maintaining a separate reels path.
        Confirmed on device: /p/{reel_code}/ lands in the post viewer.
        """
        target_type = parsed.get('type')

        if target_type in (LinkParser.TYPE_POST, LinkParser.TYPE_REEL):
            return f"https://www.instagram.com/p/{parsed['post_code']}/"
        if target_type == LinkParser.TYPE_STORY:
            url = f"https://www.instagram.com/stories/{parsed['username']}/"
            if parsed.get('story_id'):
                url += f"{parsed['story_id']}/"
            return url

        raise Exception(f'unsupported share target type: {target_type}')

    def open_target(self, parsed):
        """
        Open the target inside the Instagram app and validate it.

        Raises:
            RetryableError  temporary / our-account issue -> another account
                            should retry (order back to is_prepared=0, or the
                            action back to free).
            Exception       permanent target issue -> order gets Canceled.
        """
        d = self.device
        target_type = parsed.get('type')
        url = self.build_target_url(parsed)
        is_story = target_type == LinkParser.TYPE_STORY

        if is_story:
            # Time-critical: the 'View as X?' interstitial is up only ~3s and
            # each API call costs ~1.6s. Open WITHOUT the slow foreground
            # verify, blind-tap 'View story', then blind-tap the Share button
            # IMMEDIATELY (all inside _enter_story) so the share sheet opens
            # before the story auto-advances. The sheet, once open, has no
            # timer — so all the validation/verification happens against the
            # SHEET afterwards, not a fleeting story frame.
            self._sheet_prelaunched = False
            d.open_url(url, settle_seconds=1.5, verify=False)
            self._enter_story(url)

            # After _enter_story the share sheet should be opening. Confirm and
            # do the safety checks from that dump.
            xml = d.dump_xml()
            if d.in_browser():
                d.press_back()
                raise RetryableError('story link opened in a browser instead of Instagram')
            if d.ACT_CHALLENGE in d.foreground_activity():
                raise RetryableError('account hit a challenge screen while opening story')

            # If the share sheet is up, we're good — the story reached a
            # shareable state. If not, the story was likely gone/expired.
            if not (d.find(xml, self.SHEET_RECYCLER) or d.find(xml, self.SEARCH_FIELD)):
                self._check_target_errors(xml, target_type)
                raise RetryableError('story share sheet did not open in time')

            self._sheet_prelaunched = True
            return xml
        else:
            if not d.open_url(url, settle_seconds=7):
                if d.in_browser():
                    d.press_back()
                    raise RetryableError('target link opened in a browser instead of Instagram')
                raise RetryableError(
                    f'Instagram not in foreground after opening link ({d.foreground_package()})'
                )
            if d.ACT_CHALLENGE in d.foreground_activity():
                raise RetryableError('account hit a challenge screen while opening target')

            xml = d.dump_xml()
            self._check_target_errors(xml, target_type)

        # Verify the target is actually open by finding its share control.
        if not self._find_share_button(xml, target_type):
            # Grace retry. Two failure modes on cloud phones:
            #  - slow load: the post is coming, just wait and re-check;
            #  - the intent dropped us on the main feed (InstagramMainActivity)
            #    instead of the post — waiting won't help, so REOPEN the URL.
            for _ in range(3):
                on_feed = 'InstagramMainActivity' in d.foreground_activity()
                if on_feed:
                    self.detail('landed on feed, not the post; reopening URL')
                    d.open_url(url, settle_seconds=4)
                else:
                    time.sleep(3)

                xml = d.dump_xml()
                self._check_target_errors(xml, target_type)
                if self._find_share_button(xml, target_type):
                    break
            else:
                raise RetryableError(
                    f'{target_type} did not reach a shareable state '
                    f'(foreground: {d.foreground_activity()})'
                )

        return xml

    def _enter_story(self, url):
        """
        Get past the 'View as X?' interstitial into the story viewer.

        The interstitial is only up ~3s and a single dump_xml costs ~4s, so we
        CANNOT afford to dump-then-tap — by the time the dump returns the
        button is gone. Instead we blind-tap the fixed location of the 'View
        story' button (it sits centre-lower, ~x=540 y=1250 across dumps; the
        button is large so exact centring isn't needed) immediately after the
        page settles, then verify with a dump. If we still aren't in the
        viewer, reopen and blind-tap again a few times.
        """
        d = self.device

        for attempt in range(4):
            # Blind tap where 'View story' lives — no dump, so we hit it while
            # it's still on screen.
            d.tap(*self.VIEW_STORY_TAP)
            time.sleep(1.2)

            xml = d.dump_xml()
            if d.find(xml, self.STORY_VIEWER) or d.find(xml, {'rid': 'reel_viewer_root'}):
                self.detail(f'in story viewer (attempt {attempt + 1})')
                # If the interstitial is somehow still up, tap it properly.
                hit = d.find(xml, self.STORY_INTERSTITIAL)
                if hit:
                    d.tap(hit[0], hit[1])
                    time.sleep(1.0)
                # Blind-tap Share NOW — the story is playing and auto-advances,
                # so tap the reshare button's fixed spot without another dump.
                self.detail('tapping Share (blind)')
                d.tap(*self.STORY_RESHARE_TAP)
                time.sleep(1.5)
                return

            # Not in viewer yet: reopen the story fast and retry the blind tap.
            if attempt < 3:
                self.detail('not in viewer; reopening story')
                d.open_url(url, settle_seconds=1.5, verify=False)

    def _check_target_errors(self, xml, target_type):
        """Classify visible page text / layout, mirroring the web handlers."""
        for text in self.RETRYABLE_TEXTS:
            if self._page_contains(xml, text):
                raise RetryableError(f'temporary page issue: {text}')

        for text in self.PERMANENT_TEXTS:
            if self._page_contains(xml, text):
                raise Exception(f'target unavailable: {text}')

        # Redirect-to-profile means the content itself is not reachable
        # (an expired story lands on the owner's profile grid instead of a
        # viewer). But the story interstitial and the reel viewer themselves
        # live under reel_viewer_* and show a profile picture — so only treat
        # it as a redirect when NEITHER the interstitial nor the viewer is on
        # screen, otherwise we'd wrongly reject a perfectly good story.
        if target_type == LinkParser.TYPE_STORY:
            on_story = (self.device.find(xml, self.STORY_INTERSTITIAL)
                        or self.device.find(xml, self.STORY_VIEWER)
                        or self.device.find(xml, {'rid': 'reel_viewer_root'}))
            if not on_story and self.device.find(xml, self.PROFILE_HEADER):
                raise Exception('story expired or unavailable (redirected to profile)')
            return

        if self.device.find(xml, self.PROFILE_HEADER):
            raise Exception("post isn't accessible (redirected to profile)")

    def _find_share_button(self, xml, target_type):
        for selector in self.SHARE_BUTTONS.get(target_type, []):
            hit = self.device.find(xml, selector)
            if hit:
                return hit
        return None

    def _page_contains(self, xml, phrase):
        """Case-insensitive substring search over every node's text + desc."""
        if not xml:
            return False
        needle = phrase.lower()
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return False
        for node in root.iter('node'):
            blob = (node.get('text', '') + ' ' + node.get('content-desc', '')).lower()
            if needle in blob:
                return True
        return False

    # ── the send itself ─────────────────────────────────────────────────────
    def perform_send(self, target_type, groups_needed):
        """
        One complete send: open the sheet, tick `groups_needed` distinct
        share_group_* chats, press 'Send separately' once, verify.

        Returns the number of groups sent (== groups_needed on success).
        Raises RetryableError (incl. ShareGroupsUnavailable) on failure; the
        caller decides what to do with the order/action.
        """
        d = self.device

        # For stories the sheet was already blind-opened during open_target
        # (racing the auto-advance); for posts/reels open it now.
        if not getattr(self, '_sheet_prelaunched', False):
            self._open_sheet(target_type)
        else:
            self._sheet_prelaunched = False   # consume the flag

        selected = self._tick_groups(groups_needed)

        if len(selected) < groups_needed:
            # Leave the sheet in a sane state before bailing out.
            d.press_back()
            raise ShareGroupsUnavailable(
                f'only {len(selected)}/{groups_needed} share groups reachable on this account'
            )

        self._press_send()
        return len(selected)

    def _open_sheet(self, target_type):
        d = self.device

        xml = d.dump_xml()
        hit = self._find_share_button(xml, target_type)
        if not hit:
            raise RetryableError('share button not found on target page')

        d.tap(hit[0], hit[1])

        # Sheet is up as soon as the recipients recycler (or its search box)
        # exists. We DON'T wait for the tile count to fully stabilise here —
        # _tick_groups expands the sheet and re-reads with _read_grid_stable
        # anyway, so an extra stabilise loop would only burn expensive dumps.
        deadline = time.time() + 20
        while time.time() < deadline:
            xml = d.dump_xml()
            if d.find(xml, self.SHEET_RECYCLER) or d.find(xml, self.SEARCH_FIELD):
                return xml
            time.sleep(0.6)

        raise RetryableError('share sheet did not open')

    def _tick_groups(self, groups_needed):
        """
        Expand-and-scroll selection (on-device-proven).

        The share sheet opens short and COLLAPSES to a single recent row after
        a couple of selections, so the initial grid can only reach ~3 groups.
        Dragging the sheet's top handle up expands it full-screen; in that
        state it does NOT collapse, the Send button isn't rendered (so a tap
        can't accidentally send), and all 20 groups are scroll-reachable.

        For speed we tap EVERY visible unselected group from one dump before
        re-reading — safe here precisely because the expanded sheet doesn't
        re-lay-out under taps. Then scroll and repeat. Ground truth is still
        the dump ('Chat selected' vs 'not selected'); a missed tap is retried
        on the next pass.
        """
        d = self.device
        selected = set()

        self._expand_sheet()

        # Walk DOWN the expanded list, tapping unselected groups as we go.
        #
        # dump_xml is the expensive operation (~a few seconds each: an on-device
        # UI dump + read, both rate-limited), so this loop takes exactly ONE
        # dump per page. We read the page, tap every unselected group on it
        # WITHOUT re-dumping between taps (safe: the expanded sheet doesn't
        # re-lay-out under taps and never shows the Send button), then scroll.
        # The next iteration's single dump serves double duty — it confirms the
        # previous page's ticks AND is the new page to act on.
        seen_names = set()
        no_new_scrolls = 0
        tiles = self._read_grid_stable()    # first (and only pre-loop) dump

        for _ in range(self.MAX_GRID_ROUNDS):
            if len(selected) >= groups_needed:
                break

            for t in tiles:
                seen_names.add(t['name'])
                if t['selected']:
                    selected.add(t['name'])

            # Tap every still-unselected group on this page, back to back. No
            # extra pause between taps — the API rate-limit already spaces each
            # call ~1s apart, which is plenty for the UI to register a tick.
            to_tap = [t for t in tiles
                      if not t['selected'] and t['name'] not in selected]
            for t in to_tap[: groups_needed - len(selected)]:
                self.detail(f'tapping {t["name"]}')
                d.tap(t['x'], t['y'])
                selected.add(t['name'])   # provisional; confirmed next dump

            if len(selected) >= groups_needed:
                break

            # Scroll, then take the single dump for this page.
            before = set(seen_names)
            d.command('input swipe {} {} {} {} {}'.format(*self.SCROLL_DOWN))
            time.sleep(0.4)
            tiles = self._grid_tiles(d.dump_xml())

            # Confirm: keep only provisional names the UI actually shows ticked
            # (or that this new page hasn't re-shown as unticked); trust ticks
            # still visible. Names scrolled off-screen stay counted.
            visible = {t['name'] for t in tiles}
            confirmed_now = {t['name'] for t in tiles if t['selected']}
            selected = {s for s in selected
                        if s not in visible or s in confirmed_now}

            after = visible
            seen_names |= after
            if after - before:
                no_new_scrolls = 0
            else:
                no_new_scrolls += 1
                if no_new_scrolls >= 2:
                    self.detail('bottom of group list reached')
                    break

        self.detail(f'{len(selected)}/{groups_needed} selected from grid')

        # Fallback: search for whatever is still missing (rare with expand).
        if len(selected) < groups_needed:
            self.detail(f'searching for the remaining {groups_needed - len(selected)}')
            self._search_and_tick(selected, groups_needed)

        if len(selected) >= groups_needed:
            self._untick_extras(selected, groups_needed)

        return selected

    # ── expand / scroll helpers ─────────────────────────────────────────────
    def _expand_sheet(self):
        """Drag the bottom-sheet handle to the top so it goes full-screen."""
        self.detail('expanding share sheet')
        self.device.command('input swipe {} {} {} {} {}'.format(*self.EXPAND_SWIPE))
        time.sleep(1)

    def _tap_page_unselected(self, selected, groups_needed):
        """Kept for the probe/debug command; not used by _tick_groups now."""
        d = self.device
        progressed = False
        for t in self._grid_tiles(d.dump_xml()):
            if t['selected']:
                selected.add(t['name'])
        return progressed

    def _page_signature(self):
        """A stable id for the current scroll position: the set of visible group names."""
        return frozenset(t['name'] for t in self._grid_tiles(self.device.dump_xml()))

    def _read_grid_stable(self, retries=2):
        """
        Read the group grid, retrying briefly if a dump comes back with no
        tiles. The share sheet re-lays-out after taps (the grid slides up as
        the post preview collapses), and a dump caught mid-animation shows an
        empty recycler. A short retry rides over that transition so the caller
        never mistakes a re-layout for an empty grid.
        """
        tiles = self._grid_tiles(self.device.dump_xml())
        attempt = 0
        while not tiles and attempt < retries:
            attempt += 1
            time.sleep(0.5)
            tiles = self._grid_tiles(self.device.dump_xml())
        return tiles

    def _grid_tiles(self, xml):
        """Parse share_group_* tiles from the sheet grid, with tick state."""
        tiles = []
        if not xml:
            return tiles
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return tiles

        for node in root.iter('node'):
            rid = node.get('resource-id', '')
            if not rid.endswith(self.GRID_TILE_RID):
                continue
            desc = node.get('content-desc', '').strip()
            if not desc.startswith(self.GROUP_PREFIX):
                continue

            name = desc.split(' Chat')[0].strip()
            is_selected = desc.endswith('Chat selected')

            m = self.BOUNDS_RE.match(node.get('bounds', ''))
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())

            # Tap near the TOP of the tile (avatar area), not the geometric
            # centre. The bottom row is often clipped by the send controls, so
            # its centre can fall on 'Send separately' / 'Create group chat';
            # the avatar always sits safely inside the tile.
            x = (x1 + x2) // 2
            y = y1 + min(140, (y2 - y1) // 2)

            # Only drop tiles that are essentially off-screen (a sliver at the
            # very bottom). A clipped-but-substantial tile is still tappable.
            if (y2 - y1) < 90:
                continue

            tiles.append({'name': name, 'selected': is_selected, 'x': x, 'y': y})

        return tiles

    def _scroll_grid(self):
        # Scroll the group grid without collapsing the bottom sheet.
        # Start mid-recycler (y~1050, safely below the first tile row at
        # 306-702) and drag up to y~450, a ~600px throw entirely inside the
        # recipients area [306,1252]. A slower gesture (450ms) registers as a
        # scroll rather than a fling, so tiles don't blow past in one jump.
        self.device.command('input swipe 540 1050 540 450 450')
        time.sleep(1.0)

    def _untick_extras(self, selected, groups_needed):
        """
        Defensive: if verification ever reports more ticks than requested
        (e.g. a double-registered tap), toggle extras off so the send count
        stays exact. Extras are removed grid-first, best effort.
        """
        d = self.device
        attempts = 0
        while len(selected) > groups_needed and attempts < 6:
            attempts += 1
            xml = d.dump_xml()
            tiles = self._grid_tiles(xml)
            extra_names = list(selected)[groups_needed:]
            tapped = False
            for tile in tiles:
                if tile['selected'] and tile['name'] in extra_names:
                    d.tap(tile['x'], tile['y'])
                    d.pause(300, 600)
                    selected.discard(tile['name'])
                    tapped = True
                    break
            if not tapped:
                self._scroll_grid()
                time.sleep(1)

    def _search_and_tick(self, selected, groups_needed):
        """
        Fallback for groups the grid never surfaced.

        Confirmed on-device behaviour: after ticking ONE search result the
        sheet jumps straight back to the grid/recent view, so each search only
        buys a single group. We therefore search one exact group name at a
        time (share_group_1 .. share_group_MAX_GROUPS) and tick only the row
        whose name matches EXACTLY — a search for 'share_group_1' also lists
        11..19, and we must not tick those by mistake.

        This can mean up to MAX_GROUPS searches on a cold account, which is
        accepted for now: every group ticked lands in 'recent', so on later
        sessions the grid already shows them and the search path shrinks on
        its own.

        The field is always cleared before typing, otherwise consecutive
        queries concatenate ('share_group_1share_group_2') and match nothing.
        """
        d = self.device

        consecutive_misses = 0

        # Locate the search field ONCE and reuse its coords. It doesn't move
        # while the sheet is open, so re-finding it per group would waste a
        # dump (~2.6s) each time.
        field = d.find(d.dump_xml(), self.SEARCH_FIELD)
        if not field:
            self.detail('search field not found; cannot search groups')
            return

        for i in range(1, self.MAX_GROUPS + 1):
            if len(selected) >= groups_needed:
                break

            name = f'{self.GROUP_PREFIX}{i}'
            if name in selected:
                continue

            # Focus, CLEAR, type the exact group name (cached field coords).
            d.tap(field[0], field[1])
            d.pause(100, 200)
            d.clear_field()
            d.pause(80, 150)
            d.type_text(name)
            self.detail(f'searching {name}')

            # Let the results load, THEN hide the keyboard — on this UI the
            # result rows only render once the keyboard is dismissed (with it
            # up, the recycler shows nothing). Poll for our exact row after.
            time.sleep(1.0)
            d.press_back()
            time.sleep(0.5)

            rows = []
            for _ in range(5):
                rows = self._search_rows(d.dump_xml())
                if any(r['name'] == name for r in rows):
                    break
                time.sleep(0.6)

            exact = next((r for r in rows if r['name'] == name), None)

            # The exact row can be below the first screenful of results (a
            # search for 'share_group_1' also lists 10..19). Scroll the result
            # list a few times to bring it into view before giving up.
            scrolls = 0
            while exact is None and scrolls < 4:
                scrolls += 1
                d.command('input swipe 540 1400 540 700 400')
                time.sleep(0.7)
                rows = self._search_rows(d.dump_xml())
                exact = next((r for r in rows if r['name'] == name), None)

            if exact is None:
                consecutive_misses += 1
                if len(selected) == 0 and consecutive_misses >= 6:
                    self.detail('no share_group chats found on this account; '
                                'stopping (account not set up for share)')
                    break
                continue
            consecutive_misses = 0

            if exact['checked']:
                selected.add(name)
                continue

            self.detail(f'ticking {name} via search')
            d.tap(exact['x'], exact['y'])
            d.pause(300, 500)
            # We tapped the toggle; count it. (Re-verifying would cost an extra
            # dump per group and the sheet may have bounced to recent anyway.)
            selected.add(name)

        # Clear the search box on the way out so the grid is clean for send.
        field = d.find(d.dump_xml(), self.SEARCH_FIELD)
        if field:
            d.tap(field[0], field[1])
            d.pause(300, 600)
            d.clear_field()
            d.press_back()
            time.sleep(1)

    def _wait_search_rows(self, timeout=8):
        deadline = time.time() + timeout
        while time.time() < deadline:
            rows = self._search_rows(self.device.dump_xml())
            if rows:
                return rows
            time.sleep(0.8)
        return []

    def _search_rows(self, xml):
        """
        Parse search result rows for share_group_* chats.

        On-device the results are NOT wrapped in a single user_row_background
        container — the name (row_user_primary_name) and its checkbox
        (recipient_toggle, checkable/checked) are separate nodes that merely
        share a vertical band. So we collect every share_group_* name node and
        pair it with the recipient_toggle whose Y-centre is closest (same row),
        reading the tick state from that toggle. The tap target is the toggle
        (right side) — tapping the name can open the chat instead of ticking.
        """
        rows = []
        if not xml:
            return rows
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            return rows

        # Collect name nodes and toggle nodes with their Y centres.
        names = []      # (name, y_center, name_bounds)
        toggles = []    # (y_center, x_center, checked)
        for node in root.iter('node'):
            rid = node.get('resource-id', '')
            m = self.BOUNDS_RE.match(node.get('bounds', ''))
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            yc = (y1 + y2) // 2

            if rid.endswith(self.ROW_NAME_RID):
                txt = (node.get('text', '') or '').strip()
                if txt.startswith(self.GROUP_PREFIX):
                    names.append((txt, yc, (x1, y1, x2, y2)))
            elif rid.endswith(self.ROW_TOGGLE_RID):
                checked = node.get('checked', 'false') == 'true'
                toggles.append((yc, (x1 + x2) // 2, checked))

        for name, yc, nb in names:
            # Nearest toggle in the same row (within half a row height).
            best = None
            best_dy = 10 ** 9
            for tyc, txc, checked in toggles:
                dy = abs(tyc - yc)
                if dy < best_dy:
                    best_dy = dy
                    best = (txc, tyc, checked)
            if best and best_dy <= 90:
                txc, tyc, checked = best
                rows.append({
                    'name': name,
                    'checked': checked,
                    'x': txc,
                    'y': tyc,
                })
            else:
                # No toggle found (e.g. keyboard covering it): fall back to
                # tapping the row at the name's height, right side.
                x1, y1, x2, y2 = nb
                rows.append({
                    'name': name,
                    'checked': False,
                    'x': 960,
                    'y': (y1 + y2) // 2,
                })

        return rows

    def _find_send_button(self):
        """
        Locate the 'Send separately' button. In the EXPANDED (full-screen)
        sheet the button isn't rendered — it only appears once the sheet is in
        its shorter form. So: try as-is; if missing, collapse the sheet (drag
        the handle back down / swipe the list down to its short state) and a
        lingering keyboard is dismissed with back, then look again.
        """
        d = self.device

        hit = d.wait_for(self.SEND_BUTTON, timeout=6, interval=2)
        if hit:
            return hit

        # Dismiss a possible keyboard first.
        d.press_back()
        time.sleep(1)
        hit = d.wait_for(self.SEND_BUTTON, timeout=4, interval=2)
        if hit:
            return hit

        # Collapse the expanded sheet so the action bar with the button shows.
        # Swiping the list downward shrinks the bottom sheet back toward its
        # short form where 'Send separately' lives.
        for _ in range(3):
            d.command('input swipe {} {} {} {} {}'.format(*self.SCROLL_UP))
            time.sleep(0.5)
            hit = d.find(d.dump_xml(), self.SEND_BUTTON)
            if hit:
                return hit

        return None

    def _press_send(self):
        d = self.device

        hit = self._find_send_button()
        if not hit:
            raise RetryableError("'Send separately' button not found with groups ticked")

        d.tap(hit[0], hit[1])

        # Success = the sheet goes away (after sending only a small 'Sent'
        # toast shows). Poll until the send button and recycler are gone.
        deadline = time.time() + 20
        while time.time() < deadline:
            time.sleep(0.8)
            xml = d.dump_xml()
            if not d.find(xml, self.SEND_BUTTON) and not d.find(xml, self.SHEET_RECYCLER):
                return True
            if self._page_contains(xml, 'Sent'):
                return True

        raise RetryableError('share sheet did not close after pressing send')

    # ── planning helpers ────────────────────────────────────────────────────
    @staticmethod
    def build_send_plan(total_count, per_group, groups_per_send):
        """
        Plan the sends for an order, all decided upfront.

        Two numbers per send, because they differ:
          - groups: how many share_group_* chats to actually tick and send.
            Each group sends `per_group` REAL views no matter what, so this is
            what drives the UI.
          - count:  how much to add to the order's completed_count — the
            CUSTOMER amount, capped so the sum equals total_count exactly.
            The last send's count is whatever is left, so the customer sees
            precisely what they ordered even though more real views went out.

        Grouping rounds UP: an order needs ceil(total / per_group) groups
        total (a 100-view order still costs one whole 245-view group — sending
        extra is fine, undershooting is not). Those groups are then packed
        into sends of at most `groups_per_send`.

        Returns a list of dicts: [{'groups': int, 'count': int}, ...] with
        sum(count) == total_count.

        Examples (per_group=245, groups_per_send=20, full send = 4900):
          100    -> [{'groups': 1,  'count': 100}]
          500    -> [{'groups': 3,  'count': 500}]        # 3 groups, capped
          4900   -> [{'groups': 20, 'count': 4900}]
          5000   -> [{'groups': 20, 'count': 4900},
                     {'groups': 1,  'count': 100}]
          12000  -> [{'groups': 20, 'count': 4900},
                     {'groups': 20, 'count': 4900},
                     {'groups': 9,  'count': 2200}]
        """
        if total_count <= 0:
            return []

        # Total groups needed, rounded up (ceil without floats).
        total_groups = (total_count + per_group - 1) // per_group

        plan = []
        remaining_count = total_count
        remaining_groups = total_groups

        while remaining_groups > 0:
            groups = min(groups_per_send, remaining_groups)

            # Customer count for this send: full groups*per_group, but never
            # more than the order has left — so the final send absorbs the cap.
            count = min(groups * per_group, remaining_count)

            plan.append({'groups': groups, 'count': count})

            remaining_groups -= groups
            remaining_count -= count

        return plan