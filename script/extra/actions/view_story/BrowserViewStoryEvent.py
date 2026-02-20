from script.extra.helper import go_to_page
from script.models.OrderAction import get_next_action_for_account, mark_action_completed, mark_action_failed, release_stuck_actions, deduct_balance
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from .LinkParser import LinkParser
import time


class BrowserViewStoryEvent(BaseAction):
    command = None
    action = None
    order = None
    parsed_link = None
    target_username = None
    story_seen_count = 0
    response_listener_active = False

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
        self.pick_and_mark_action()

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

            if self.order.status == 'Canceled':
                self.action.status = 'failed'
                self.action.save()
            else:
                self.mark_action_failed_with_charge()

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.ig.account.add_cli(f'ERROR - {str(e)}', print_only=True)
            self.action.reset_to_free()

            if self.command:
                self.command.update_cmd('state', 'fail')

    def pick_and_mark_action(self):
        self.action = get_next_action_for_account(self.ig.account, ['view_story'])

        if not self.action:
            raise Exception('There is no view_story order')

        self.order = self.action.order

        self.ig.account.add_cli(f'Order: {self.order.id} | Target: {self.order.target_link}', print_only=True)

        if self.order.status == 'Pending':
            self.order.set_status_to('In progress')

    def parse_and_validate_link(self):
        self.parsed_link = LinkParser.parse(self.order.target_link)

        # Reject highlights - not supported
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

    def view_specific_story(self):
        """View a specific story from direct URL"""
        story_url = self.order.target_link

        self.setup_response_listener()

        go_to_page(self.ig, story_url, 'Story Page')
        self.ig.pause(3000, 4000)

        self.click_view_story_button()
        self.check_story_fail_situations()
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
        self.ig.pause(3000, 4000)

        # Check for no story situations
        if self.ig.is_visible_by_text("This story is unavailable"):
            self.remove_response_listener()
            raise Exception("Story unavailable")

        if self.ig.is_visible_by_text("No stories available"):
            self.remove_response_listener()
            return

        self.click_view_story_button()
        self.check_story_fail_situations()
        self.wait_for_story_view()

    def check_story_fail_situations(self):
        if self.ig.is_visible_by_text("This story is unavailable"):
            self.fail_order_with_full_charge("Story is unavailable")
            raise LinkIsNotCorrect("Story is unavailable")

        if self.ig.is_visible_by_text("Sorry, this page isn't available"):
            self.fail_order_with_full_charge("Story not found")
            raise LinkIsNotCorrect("Story not found")

    def fail_order_with_full_charge(self, message):
        """Fail the entire order and deduct balance for all actions"""
        from script.models.Balance import Balance
        from script.models.Order import Order
        from script.models.OrderAction import OrderAction
        from decimal import Decimal

        db = Order._meta.database

        try:
            with db.atomic():
                order = (
                    Order
                    .select()
                    .where(Order.id == self.order.id)
                    .for_update()
                    .first()
                )

                if order.status == 'Canceled':
                    return

                order.status = 'Canceled'
                order.description = message
                order.save()

                self.order.status = 'Canceled'

                (
                    OrderAction
                    .update(status='failed')
                    .where(
                        (OrderAction.order == self.order.id) &
                        (OrderAction.status == 'free')
                    )
                    .execute()
                )

                rate = Decimal('0.000025')
                total_charge = Decimal(order.total_count) * rate

                balance = Balance.get(Balance.customer == 'sadeghi')
                balance.balance = balance.balance - total_charge
                balance.save()

        except Exception as e:
            self.ig.account.add_cli(f"Failed to charge order: {e}", print_only=True)

    def wait_for_story_view(self):
        """Wait for Instagram to confirm story view"""
        current_url = self.ig.page.url

        if '/stories/' not in current_url:
            self.remove_response_listener()
            raise Exception(f"Not in story page")

        story_confirmed = self.wait_for_story_seen(timeout=30)

        if not story_confirmed:
            self.remove_response_listener()
            self.force_exit_story()
            raise Exception("Story not viewed - no confirmation")

        self.remove_response_listener()
        self.force_exit_story()

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
        release_stuck_actions()

    def mark_action_failed_with_charge(self):
        mark_action_failed(self.action)
        deduct_balance('view_story')
        release_stuck_actions()