from script.extra.helper import go_to_page
from script.models.OrderAction import get_single_action_for_account, mark_action_completed, mark_action_failed, deduct_balance, OrderAction
from script.models.Order import Order
from script.models.Balance import Balance
from script.models.Setting import Setting
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from .LinkParser import LinkParser
from decimal import Decimal
import time


class BrowserViewStoryEvent(BaseAction):
    command = None
    action = None
    order = None
    parsed_link = None
    target_username = None
    story_seen_count = 0
    response_listener_active = False
    processed_order_ids = []

    def setup_response_listener(self):
        """Setup listener for story seen responses"""
        self.story_seen_count = 0
        self.response_listener_active = True
        self.ig.page.on("response", self.handle_response)

    def remove_response_listener(self):
        """Remove response listener"""
        try:
            self.response_listener_active = False
            self.ig.page.remove_listener("response", self.handle_response)
        except:
            pass

    def handle_response(self, response):
        """Handle network responses to detect story seen"""
        if not self.response_listener_active:
            return

        try:
            if '/graphql/query' not in response.url:
                return

            json_response = response.json()

            if 'data' in json_response:
                data = json_response['data']
                if 'xdt_api__v1__stories__reel__seen' in data:
                    self.story_seen_count += 1
        except:
            pass

    def wait_for_story_seen(self, timeout=30):
        """Wait for story seen response with timeout"""
        if self.story_seen_count > 0:
            return True

        start = time.time()
        while time.time() - start < timeout:
            if self.story_seen_count > 0:
                return True
            time.sleep(0.3)

        return False

    def init(self):
        batch_size = int(Setting.get_value('view_story_batch_size', 1))
        self.processed_order_ids = []

        for i in range(batch_size):
            action = get_single_action_for_account(
                self.ig.account,
                ['view_story'],
                excluded_order_ids=self.processed_order_ids
            )

            if not action:
                if i == 0:
                    raise Exception('There is no view_story order')
                break

            self.action = action
            self.order = action.order
            self.processed_order_ids.append(self.order.id)

            self.ig.account.add_cli(f'Picked action #{i+1} for order {self.order.id}', print_only=True)
            self.process_single_action()

        self.force_exit_story()

    def process_single_action(self):
        self.ig.account.add_cli(f'Order: {self.order.id} | Target: {self.order.target_link}', print_only=True)

        try:
            self.command = self.ig.account.create_command('view story', 'processing')

            self.parse_and_validate_link()

            if self.parsed_link['type'] == LinkParser.TYPE_STORY:
                self.view_specific_story()
            else:
                self.view_first_story()

            self.mark_action_sent()
            self.command.update_cmd('state', 'success')
            self.ig.account.add_cli('SUCCESS - Story viewed', print_only=True)
            self.ig.pause(1500, 2000)

        except LinkIsNotCorrect as e:
            self.ig.account.add_cli(f'FAILED - Link error: {str(e)}', print_only=True)
            self._handle_link_error()

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.ig.account.add_cli(f'ERROR - {str(e)}', print_only=True)
            self._safe_reset_to_free()

            if self.command:
                self.command.update_cmd('state', 'fail')

        finally:
            self.remove_response_listener()

    def _handle_link_error(self):
        """Handle link errors - check if order is canceled first"""
        refreshed_order = Order.select(Order.status).where(Order.id == self.order.id).first()

        if refreshed_order and refreshed_order.status == 'Canceled':
            OrderAction.update(
                status='failed'
            ).where(
                OrderAction.id == self.action.id
            ).execute()
        else:
            self.mark_action_failed_with_charge()

    def _safe_reset_to_free(self):
        """Safely reset action to free status"""
        try:
            OrderAction.update(
                status='free',
                account=None
            ).where(
                (OrderAction.id == self.action.id) &
                (OrderAction.status == 'processing')
            ).execute()
        except Exception as e:
            self.ig.account.add_cli(f'Error resetting action: {e}', print_only=True)

    def parse_and_validate_link(self):
        self.parsed_link = LinkParser.parse(self.order.target_link)

        if self.parsed_link['type'] == LinkParser.TYPE_HIGHLIGHT:
            raise LinkIsNotCorrect("Highlights are not supported")

        if self.parsed_link['type'] == LinkParser.TYPE_STORY:
            self.target_username = self.parsed_link['username']
            return

        if self.parsed_link['username']:
            self.target_username = self.parsed_link['username']
            return

        if LinkParser.needs_username_extraction(self.order.target_link):
            self.target_username = self.extract_username_from_post()
            return

        raise LinkIsNotCorrect("Could not determine username from link")

    def extract_username_from_post(self):
        """Extract username from post/reel page"""
        go_to_page(self.ig, self.order.target_link, 'Post Page')
        self.ig.pause(3000, 4000)

        self.check_page_not_available()

        username = self.click_and_extract_username()

        if username:
            return username

        raise LinkIsNotCorrect("Could not extract username from post")

    def click_and_extract_username(self):
        """Extract username from profile link href"""
        profile_selectors = [
            'a._a6hd[href*="/reels/"]',
            'a[href*="/reels/"][role="link"]',
            'div._aaqt a[href^="/"][role="link"]',
            'div._aaqt a._a6hd[href^="/"]',
            'a[href^="/"][role="link"]:has(span._ap3a)',
            'a.notranslate[href^="/"][role="link"]',
            'header a[href^="/"][role="link"]',
            'article header a[href^="/"]',
            'div.x78zum5 a[href^="/"][role="link"]',
            'a._a6hd[href^="/"][role="link"]',
            'a[role="link"][href^="/"]',
        ]

        for selector in profile_selectors:
            try:
                elements = self.ig.page.locator(selector)
                count = elements.count()

                for i in range(min(count, 5)):
                    element = elements.nth(i)
                    if element.is_visible():
                        href = element.get_attribute('href', timeout=3000)
                        if href:
                            username = self.extract_username_from_href(href)
                            if username:
                                return username
            except:
                continue

        return None

    def extract_username_from_href(self, href):
        """Extract clean username from href"""
        if not href or href == '#':
            return None

        href = href.lstrip('/')
        parts = href.split('/')
        if not parts:
            return None

        username = parts[0]

        if '?' in username:
            username = username.split('?')[0]

        reserved = ['p', 'reel', 'reels', 'stories', 'explore', 'direct', 'accounts', 'tv', 'tags', 'locations']
        if username.lower() in reserved:
            return None

        if not username or len(username) > 30:
            return None

        import re
        if not re.match(r'^[a-zA-Z0-9_.]+$', username):
            return None

        return username

    def wait_for_page_load(self, page_type='profile', timeout=10):
        """
        Wait for page to load and check for errors.
        Returns: 'loaded', 'error', or 'timeout'
        """
        if page_type == 'profile':
            success_selectors = [
                'button._aswp',
                'svg[aria-label="Posts"]',
                'div[role="tablist"]',
            ]
        elif page_type == 'story':
            success_selectors = [
                'svg[aria-label="Like"]',
                'div[aria-label="Toggle audio"]',
                'svg[aria-label="Audio is muted"]',
            ]
        else:
            success_selectors = []

        error_texts = [
            "There's an issue and the page could not be loaded",
        ]

        start = time.time()
        while time.time() - start < timeout:
            # Check for error first
            for text in error_texts:
                if self.ig.is_visible_by_text(text):
                    return 'error'

            # Check for success elements
            for selector in success_selectors:
                try:
                    element = self.ig.page.locator(selector).first
                    if element.count() > 0 and element.is_visible():
                        return 'loaded'
                except:
                    continue

            time.sleep(0.5)

        return 'timeout'

    def check_page_load_error(self):
        """
        Check if page failed to load completely.
        This means Instagram couldn't load the page at all - fail immediately.
        """
        error_texts = [
            "There's an issue and the page could not be loaded",
        ]

        for text in error_texts:
            if self.ig.is_visible_by_text(text):
                self.fail_order_with_full_charge(f"Page load error: {text}")
                raise LinkIsNotCorrect(text)

    def view_specific_story(self):
        """View a specific story from direct URL"""
        story_url = self.order.target_link

        self.setup_response_listener()

        go_to_page(self.ig, story_url, 'Story Page')
        self.ig.pause(5000, 6000)

        # Check for page load error FIRST - fail immediately
        self.check_page_load_error()

        # Check if redirected away from story
        current_url = self.ig.page.url
        if '/stories/' not in current_url:
            self.remove_response_listener()
            self.handle_no_story_redirect()
            return

        self.check_story_unavailable()

        self.click_view_story_button()
        self.check_story_unavailable()
        self.wait_for_story_view()

    def click_view_story_button(self):
        """Click View story button with retry loop"""
        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            attempt += 1

            # Check if already in story
            if '/stories/' in self.ig.page.url and 'View story' not in self.ig.page.content():
                return True

            clicked = self._try_click_view_story()

            if clicked:
                self.ig.pause(1500, 2000)

                if '/stories/' in self.ig.page.url:
                    try:
                        button = self.ig.page.locator('div[role="button"]:has-text("View story")').first
                        if button.count() == 0 or not button.is_visible():
                            return True
                    except:
                        return True
            else:
                self.ig.pause(1000, 1500)

        return False

    def _try_click_view_story(self):
        """Single attempt to click view story button"""
        selectors = [
            'div.x1i10hfl[role="button"]:has-text("View story")',
            'div[role="button"]:has-text("View story")',
            'button:has-text("View story")',
            ':text("View story")',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=5000)
                    return True
            except:
                continue

        try:
            button = self.ig.page.get_by_role("button", name="View story")
            if button.count() > 0 and button.is_visible():
                button.click(timeout=5000)
                return True
        except:
            pass

        try:
            button = self.ig.page.get_by_text("View story", exact=True)
            if button.count() > 0 and button.is_visible():
                button.click(timeout=5000)
                return True
        except:
            pass

        return False

    def view_first_story(self):
        """View first story using direct URL"""
        story_url = f"https://www.instagram.com/stories/{self.target_username}/"

        # Reset listener to ensure clean state (important for post/reel flow)
        self.remove_response_listener()
        self.setup_response_listener()

        go_to_page(self.ig, story_url, 'Story Page')
        self.ig.pause(5000, 6000)

        # Check for page load error FIRST - fail immediately
        self.check_page_load_error()

        # Check if redirected to profile (user has no story)
        current_url = self.ig.page.url
        if '/stories/' not in current_url:
            self.remove_response_listener()
            self.handle_no_story_redirect()
            return

        self.check_story_unavailable()

        self.click_view_story_button()
        self.check_story_unavailable()
        self.wait_for_story_view()

    def handle_no_story_redirect(self):
        """
        Handle when redirected to profile instead of story page.
        If completed_count > 0, verify by checking story ring on profile.
        """
        # Refresh order to get latest completed_count
        refreshed_order = Order.select(Order.completed_count).where(Order.id == self.order.id).first()
        completed_count = refreshed_order.completed_count if refreshed_order else 0

        if completed_count == 0:
            # First attempt - probably no story
            self.fail_order_with_full_charge("User has no active story")
            raise LinkIsNotCorrect("User has no active story")

        # completed_count > 0, others succeeded before - check profile for story ring
        self.ig.account.add_cli(f'Completed count is {completed_count}, checking profile for story ring...', print_only=True)

        profile_url = f"https://www.instagram.com/{self.target_username}/"
        go_to_page(self.ig, profile_url, 'Profile Page')
        self.ig.pause(3000, 4000)

        # Wait for profile page to load
        page_status = self.wait_for_page_load(page_type='profile', timeout=10)

        if page_status == 'error':
            # Page load error - fail immediately
            self.fail_order_with_full_charge("Page load error")
            raise LinkIsNotCorrect("There's an issue and the page could not be loaded")

        if page_status == 'timeout':
            # Could not determine - reset to free for retry
            self.ig.account.add_cli('Profile page load timeout - resetting action to free', print_only=True)
            self._safe_reset_to_free()
            raise Exception("Profile page load timeout - reset to free")

        # Page loaded successfully, now check for story ring
        if self.has_story_ring():
            # Story exists, problem is with this account
            self.ig.account.add_cli('Story ring found - resetting action to free', print_only=True)
            self._safe_reset_to_free()
            raise Exception("Story exists but could not load - reset to free")
        else:
            # No story ring - story actually expired/removed
            self.ig.account.add_cli('No story ring found - story expired', print_only=True)
            self.fail_order_with_full_charge("Story has expired")
            raise LinkIsNotCorrect("Story has expired")

    def has_story_ring(self):
        """Check if profile has story ring (colored circle around avatar)"""
        story_ring_selectors = [
            'canvas.x1upo8f9',
            'section canvas[height="135"]',
            'section canvas[width="135"]',
            'header canvas',
        ]

        for selector in story_ring_selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    return True
            except:
                continue

        return False

    def check_story_unavailable(self):
        """
        Check all possible story unavailable situations.
        All these are client errors - charge the full order.
        """
        current_url = self.ig.page.url

        # Check URL for unavailable indicator
        if 'show_story_unavailable=1' in current_url:
            self.fail_order_with_full_charge("Story is unavailable")
            raise LinkIsNotCorrect("Story is unavailable (URL redirect)")

        # Check page texts for unavailable states
        unavailable_texts = [
            "This story is unavailable",
            "Sorry, this page isn't available",
            "Page is not available",
            "This page isn't available",
            "No stories available",
            "The link you followed may be broken",
            "the page may have been removed",
        ]

        for text in unavailable_texts:
            if self.ig.is_visible_by_text(text):
                self.fail_order_with_full_charge(f"Story unavailable: {text}")
                raise LinkIsNotCorrect(text)

    def check_page_not_available(self):
        """
        Check if page (post/reel/profile) is not available.
        Used when extracting username from post/reel.
        """
        unavailable_texts = [
            "Sorry, this page isn't available",
            "Page is not available",
            "This page isn't available",
            "The link you followed may be broken",
            "the page may have been removed",
            "Post isn't available",
            "There's an issue and the page could not be loaded",
        ]

        for text in unavailable_texts:
            if self.ig.is_visible_by_text(text):
                self.fail_order_with_full_charge(f"Page unavailable: {text}")
                raise LinkIsNotCorrect(text)

    def fail_order_with_full_charge(self, message):
        """
        Fail the entire order and deduct balance for all actions.
        All UPDATEs are atomic - no transaction needed, no FOR UPDATE.
        Actions stay free/sent - not failed - so order can be reset later.
        """
        from script.models.OrderAction import ACTION_RATES

        try:
            # Cancel order atomically
            updated = Order.update(
                status='Canceled',
                description=message
            ).where(
                (Order.id == self.order.id) &
                (Order.status != 'Canceled')
            ).execute()

            if updated == 0:
                return

            self.order.status = 'Canceled'

            # Reset processing actions to free (not failed)
            OrderAction.update(
                status='free',
                account=None
            ).where(
                (OrderAction.order == self.order.id) &
                (OrderAction.status == 'processing')
            ).execute()

            # Deduct balance atomically
            rate = ACTION_RATES.get(self.order.service_type, Decimal('0.00005'))
            total_charge = Decimal(self.order.total_count) * rate

            Balance.update(
                balance=Balance.balance - total_charge
            ).where(
                Balance.customer == 'sadeghi'
            ).execute()

        except Exception as e:
            self.ig.account.add_cli(f"Failed to charge order: {e}", print_only=True)

    def wait_for_story_view(self):
        """Wait for Instagram to confirm story view"""
        current_url = self.ig.page.url

        if '/stories/' not in current_url:
            self.remove_response_listener()
            self.handle_no_story_redirect()
            return

        story_confirmed = self.wait_for_story_seen(timeout=30)

        if not story_confirmed:
            self.remove_response_listener()
            raise Exception("Story not viewed - no confirmation")

    def force_exit_story(self):
        """Force exit from story"""
        try:
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(200, 300)

            if '/stories/' in self.ig.page.url:
                close_selectors = [
                    'svg[aria-label="Close"]',
                    'div[role="button"]:has(svg[aria-label="Close"])',
                ]
                for selector in close_selectors:
                    try:
                        btn = self.ig.page.locator(selector).first
                        if btn.count() > 0 and btn.is_visible():
                            btn.click(timeout=2000)
                            break
                    except:
                        continue

            self.ig.pause(200, 300)
        except:
            pass

    def mark_action_sent(self):
        mark_action_completed(self.action)
        deduct_balance('view_story')

    def mark_action_failed_with_charge(self):
        mark_action_failed(self.action)
        deduct_balance('view_story')