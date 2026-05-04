import re
import random
import time
from script.extra.helper import go_to_page, tehran_now
from script.models.AccountTemplate import AccountTemplate
from script.models.Template import Template


SHORTCODE_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

# How long to wait for the insights GraphQL response before giving up
INSIGHTS_CAPTURE_TIMEOUT = 30

FRIENDLY_NAME = 'PolarisMediaInsightsBaseSurfaceQuery'

# Chance of performing optional human-like actions (10-15%)
SCROLL_CHANCE_MIN = 0.10
SCROLL_CHANCE_MAX = 0.15


class BrowserPostInsightsEvent:
    def __init__(self, ig):
        self.ig = ig
        self.insights_data = None
        self.listener = None
        # Roll the scroll chance once per session so it stays consistent
        self.scroll_chance = random.uniform(SCROLL_CHANCE_MIN, SCROLL_CHANCE_MAX)

    def init(self):
        self.ig.account.add_cli('[PostInsights] Starting post insights collection')

        posts = self._get_posts()

        if not posts:
            self.ig.account.add_cli('[PostInsights] No custom completed posts with URL found')
            return

        self.ig.account.add_cli(f'[PostInsights] Found {len(posts)} posts to process')

        for index, at in enumerate(posts):
            try:
                self._process_single_post(at, index + 1, len(posts))
            except Exception as e:
                self.ig.account.add_cli(f'[PostInsights] Error processing post #{at.id}: {str(e)}')
                continue

        self.ig.account.add_cli('[PostInsights] Finished processing all posts')

    def _get_posts(self):
        """Fetch all custom completed templates with a URL for this account, newest first."""
        return list(
            AccountTemplate
            .select(
                AccountTemplate.id,
                AccountTemplate.account,
                AccountTemplate.template,
                AccountTemplate.url,
            )
            .join(Template)
            .where(
                (AccountTemplate.account == self.ig.account.id) &
                (Template.is_custom == True) &
                (AccountTemplate.status == 'completed') &
                (AccountTemplate.url.is_null(False))
            )
            .order_by(AccountTemplate.id.desc())
        )

    def _process_single_post(self, at, current, total):
        url = at.url
        shortcode = self._extract_shortcode(url)

        if not shortcode:
            self.ig.account.add_cli(f'[PostInsights] Could not extract shortcode from: {url}')
            return

        self.ig.account.add_cli(f'[PostInsights] ({current}/{total}) Processing: {url}')

        # Step 1: Navigate to the post page to verify it exists
        self._go_to_post_page(url)

        if not self._is_on_post_page():
            self.ig.account.add_cli(f'[PostInsights] Post not available, skipping: {url}')
            return

        self._dismiss_popup()
        self._maybe_scroll_page()
        self.ig.pause(3000, 8000)

        # Step 2: Read basic metrics from the post page DOM
        dom_metrics = self._read_dom_metrics()
        self.ig.account.add_cli(
            f'[PostInsights] DOM metrics: likes={dom_metrics["like_count"]}, '
            f'comments={dom_metrics["comment_count"]}, reposts={dom_metrics["repost_count"]}'
        )

        # Save DOM metrics as a baseline (works even for personal accounts)
        self._save_dom_metrics(at, dom_metrics)

        # Step 3: Calculate media_id and navigate to insights page
        media_id = self._shortcode_to_media_id(shortcode)
        self.ig.account.add_cli(f'[PostInsights] media_id: {media_id}')

        self.insights_data = None
        self._setup_insights_listener()

        insights_url = f'https://www.instagram.com/insights/media/{media_id}/'
        go_to_page(self.ig, insights_url, 'Insights Page')
        self.ig.pause(3000, 5000)

        # Step 4: Check if insights page is available (professional accounts only)
        if self._is_insights_unavailable():
            self.ig.account.add_cli('[PostInsights] Insights page not available, personal account or restricted')
            self._remove_listener()
            self.ig.pause(2000, 5000)
            return

        # Step 5: Wait for the insights response to be captured
        captured = self._wait_for_insights_capture()
        self._remove_listener()

        if not captured:
            self.ig.account.add_cli('[PostInsights] Timeout waiting for insights data, skipping')
            return

        # Step 6: Parse insights and override the DOM metrics with full data
        self._save_insights(at, self.insights_data)

        # Step 7: Random delay on insights page before moving to next
        self._maybe_scroll_insights()
        self.ig.pause(5000, 12000)


    def _extract_shortcode(self, url):
        """Extract shortcode from /p/, /reel/, or /reels/ URL format."""
        match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    def _shortcode_to_media_id(self, shortcode):
        """Convert Instagram shortcode to numeric media_id using base64 decoding."""
        media_id = 0
        for char in shortcode:
            media_id = media_id * 64 + SHORTCODE_ALPHABET.index(char)
        return str(media_id)


    def _go_to_post_page(self, url):
        go_to_page(self.ig, url, 'Post Page')
        self.ig.pause(4000, 6000)

    def _is_on_post_page(self):
        """Check if we are actually on a post page and the post is accessible."""
        current_url = self.ig.page.url

        if '/p/' not in current_url and '/reel/' not in current_url and '/reels/' not in current_url:
            self.ig.account.add_cli(f'[PostInsights] Redirected away from post: {current_url}')
            return False

        error_texts = [
            "Post isn't available",
            "The link may be broken",
            "the profile may have been removed",
            "Sorry, this page isn't available",
            "Page is not available",
            "This page isn't available",
            "This account is private",
            "This profile is private",
        ]

        for text in error_texts:
            if self.ig.is_visible_by_text(text):
                self.ig.account.add_cli(f'[PostInsights] Post error detected: {text}')
                return False

        return True

    def _is_insights_unavailable(self):
        """Check if insights page shows an error (personal account or deleted post)."""
        error_texts = [
            "Sorry, this page isn't available",
            "Page is not available",
            "This page isn't available",
            "The link you followed may be broken",
        ]

        for text in error_texts:
            if self.ig.is_visible_by_text(text):
                return True

        return False

    def _dismiss_popup(self):
        """Close any popup that might appear on the post page."""
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(1000, 2000)
            except Exception:
                pass


    def _read_dom_metrics(self):
        """
        Read like_count, comment_count, and repost_count from the post page DOM.
        Uses JavaScript to find the count span that immediately follows each SVG icon.
        The DOM pattern on the post page action bar is:
          [svg aria-label="Like"] -> count span -> [svg "Comment"] -> count span -> ...
        Each count span has role="button" and class "x1s688f".
        Returns dict with integer values, 0 if not found.
        """
        try:
            raw = self.ig.page.evaluate('''() => {
                const result = {like: '', comment: '', repost: ''};
                const section = document.querySelector('section');
                if (!section) return result;

                // Get all spans with role="button" and the count class inside the section
                const spans = section.querySelectorAll('span[role="button"].x1s688f');

                // Map each SVG label to its icon element position
                const labels = ['Like', 'Unlike', 'Comment', 'Repost'];
                const icons = {};
                for (const label of labels) {
                    const svg = section.querySelector(`svg[aria-label="${label}"]`);
                    if (svg) {
                        // Normalize Like/Unlike to just "like"
                        const key = (label === 'Unlike') ? 'Like' : label;
                        if (!icons[key]) icons[key] = svg;
                    }
                }

                // For each count span, find which icon it belongs to by checking
                // which icon appears closest before it in document order
                for (const span of spans) {
                    const text = span.textContent.trim();
                    if (!text || text.length > 10) continue;

                    // Check which icon is the nearest preceding sibling/ancestor
                    let node = span;
                    let found = false;
                    // Walk backwards through previous siblings and their children
                    while (node && !found) {
                        const prev = node.previousElementSibling;
                        if (prev) {
                            for (const [label, iconEl] of Object.entries(icons)) {
                                if (prev.contains(iconEl) || prev === iconEl) {
                                    const key = label.toLowerCase();
                                    if (!result[key]) result[key] = text;
                                    found = true;
                                    break;
                                }
                            }
                            node = prev;
                        } else {
                            node = node.parentElement;
                        }
                    }
                }

                return result;
            }''')

            return {
                'like_count': self._parse_count_text(raw.get('like', '')),
                'comment_count': self._parse_count_text(raw.get('comment', '')),
                'repost_count': self._parse_count_text(raw.get('repost', '')),
            }

        except Exception as e:
            self.ig.account.add_cli(f'[PostInsights] Error reading DOM metrics: {str(e)}')
            return {'like_count': 0, 'comment_count': 0, 'repost_count': 0}

    def _parse_count_text(self, text):
        """
        Parse Instagram count text to an integer.
        Handles: "429", "17.3K", "1.2M", "2B", comma-separated numbers, etc.
        """
        text = text.strip().replace(',', '')

        if not text:
            return 0

        multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
        upper = text.upper()
        last_char = upper[-1]

        if last_char in multipliers:
            try:
                return int(float(upper[:-1]) * multipliers[last_char])
            except ValueError:
                return 0

        try:
            return int(text)
        except ValueError:
            return 0


    def _setup_insights_listener(self):
        """Attach a response listener that captures the insights GraphQL response."""
        def on_response(response):
            if self.insights_data:
                return

            try:
                url = response.url

                if '/graphql/query' not in url and '/api/graphql' not in url:
                    return

                headers = response.request.headers
                friendly_name = headers.get('x-fb-friendly-name', '')

                if friendly_name != FRIENDLY_NAME:
                    return

                json_data = response.json()
                media_data = json_data.get('data', {}).get('media')

                if media_data:
                    self.insights_data = media_data
                    self.ig.account.add_cli('[PostInsights] Insights response captured')

            except Exception as e:
                self.ig.account.add_cli(f'[PostInsights] Listener error: {str(e)}')

        self.listener = on_response
        self.ig.page.on('response', self.listener)

    def _remove_listener(self):
        """Remove the response listener to avoid stacking across posts."""
        if self.listener:
            try:
                self.ig.page.remove_listener('response', self.listener)
            except Exception:
                pass
            self.listener = None

    def _wait_for_insights_capture(self):
        """Wait until insights data is captured or timeout is reached."""
        start = time.time()
        last_log = start

        while time.time() - start < INSIGHTS_CAPTURE_TIMEOUT:
            if self.insights_data:
                elapsed = round(time.time() - start, 1)
                self.ig.account.add_cli(f'[PostInsights] Capture done in {elapsed}s')
                return True

            now = time.time()
            if now - last_log >= 10:
                self.ig.account.add_cli(f'[PostInsights] Waiting for capture ({int(now - start)}s)')
                last_log = now

            time.sleep(0.3)

        return False


    def _save_dom_metrics(self, at, metrics):
        """Save the basic metrics extracted from post page DOM."""
        AccountTemplate.update(
            like_count=metrics['like_count'],
            comment_count=metrics['comment_count'],
            repost_count=metrics['repost_count'],
            updated_at=tehran_now()
        ).where(
            AccountTemplate.id == at.id
        ).execute()

        self.ig.account.add_cli(f'[PostInsights] DOM metrics saved for post #{at.id}')

    def _save_insights(self, at, raw_data):
        """
        Parse the captured insights response and override metrics in the database.
        Note: repost_count is NOT updated here because the API field umapi_reshares_count
        represents Shares (DM sends), not Reposts. Repost count only comes from DOM extraction.
        """
        likes = self._extract_metric(raw_data, 'umapi_likes_count')
        comments = self._extract_metric(raw_data, 'umapi_comments_count')
        views = self._extract_metric(raw_data, 'umapi_unified_total_content_views_count')
        saves = self._extract_metric(raw_data, 'umapi_saves_count')

        AccountTemplate.update(
            like_count=likes,
            comment_count=comments,
            view_count=views,
            save_count=saves,
            stats=raw_data,
            updated_at=tehran_now()
        ).where(
            AccountTemplate.id == at.id
        ).execute()

        self.ig.account.add_cli(
            f'[PostInsights] Insights saved: likes={likes}, comments={comments}, '
            f'views={views}, saves={saves}'
        )

    def _extract_metric(self, data, key):
        """
        Safely extract a single metric value from the insights response.
        Each metric follows the pattern: { "value": { "results": [{ "total_value": N }] } }
        Returns 0 if not found or if the results array is empty.
        """
        try:
            results = data.get(key, {}).get('value', {}).get('results', [])
            if results:
                return results[0].get('total_value', 0)
        except (AttributeError, IndexError, TypeError):
            pass
        return 0


    def _should_scroll(self):
        """Return True roughly 10-15% of the time."""
        return random.random() < self.scroll_chance

    def _maybe_scroll_page(self):
        """Occasionally scroll the post page to simulate reading behavior."""
        if not self._should_scroll():
            return
        self._smooth_scroll(random.randint(100, 600))

    def _maybe_scroll_insights(self):
        """Occasionally scroll inside the insights sidebar."""
        if not self._should_scroll():
            return

        amount = random.randint(150, 500)

        try:
            # Find the scrollable insights container by walking up from the "Views" heading
            self.ig.page.evaluate('''(scrollAmount) => {
                const headings = document.querySelectorAll('h3');
                for (const h of headings) {
                    if (h.textContent.trim() === 'Views') {
                        let el = h.parentElement;
                        while (el) {
                            if (el.scrollHeight > el.clientHeight + 10) {
                                const steps = 5 + Math.floor(Math.random() * 4);
                                const stepSize = scrollAmount / steps;
                                let i = 0;
                                const interval = setInterval(() => {
                                    el.scrollBy(0, stepSize + (Math.random() * 6 - 3));
                                    i++;
                                    if (i >= steps) clearInterval(interval);
                                }, 60 + Math.floor(Math.random() * 40));
                                return;
                            }
                            el = el.parentElement;
                        }
                    }
                }
            }''', amount)
            self.ig.pause(800, 2000)
        except Exception:
            self._smooth_scroll(amount)

    def _smooth_scroll(self, total_amount):
        """
        Scroll the main page in small incremental steps to look more natural.
        Each step has a slightly different size and a small random delay between them.
        """
        steps = random.randint(3, 7)
        base_step = total_amount / steps

        for i in range(steps):
            # Each step varies a bit from the base size
            jitter = random.uniform(-0.3, 0.3) * base_step
            step_amount = max(10, base_step + jitter)
            self.ig.page.mouse.wheel(0, step_amount)
            # Small random pause between scroll steps (40-120ms)
            self.ig.page.wait_for_timeout(random.randint(40, 120))

        self.ig.pause(300, 800)