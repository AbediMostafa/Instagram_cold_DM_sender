from script.extra.helper import go_to_page
from script.models.OrderAction import get_next_action_for_account, mark_action_completed, mark_action_failed, deduct_balance
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from .LinkParser import LinkParser
import time
import os
import threading
from datetime import datetime

file_lock = threading.Lock()


class BrowserViewAllStoriesEvent(BaseAction):
    command = None
    action = None
    order = None
    parsed_link = None
    target_username = None
    story_seen_count = 0
    total_stories_viewed = 0
    response_listener_active = False
    log_file = None

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        account_id = self.ig.account.id if self.ig and self.ig.account else "?"
        log_line = f"[{timestamp}] [Account:{account_id}] {message}\n"

        with file_lock:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_line)
            except:
                pass

    def init_log_file(self):
        base_path = r"C:\Users\Public\Desktop\project\logs"

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        self.log_file = f"{base_path}\\order_{self.order.id}.log"

    def setup_response_listener(self):
        self.story_seen_count = 0
        self.response_listener_active = True
        self.ig.page.on("response", self.handle_response)

    def remove_response_listener(self):
        try:
            self.response_listener_active = False
            self.ig.page.remove_listener("response", self.handle_response)
        except:
            pass

    def handle_response(self, response):
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
                    self.total_stories_viewed += 1
                    self.log(f"SEEN response received (count: {self.story_seen_count}, total: {self.total_stories_viewed})")
        except:
            pass

    def wait_for_story_seen(self, timeout=30):
        if self.story_seen_count > 0:
            return True

        start = time.time()
        while time.time() - start < timeout:
            if self.story_seen_count > 0:
                return True
            time.sleep(0.3)

        return False

    def reset_seen_count(self):
        self.story_seen_count = 0

    def init(self):
        self.pick_and_mark_action()
        self.init_log_file()

        self.log(f"START - Order: {self.order.id} | Target: {self.order.target_link}")

        try:
            self.command = self.ig.account.create_command('view all stories', 'processing')

            self.parse_and_validate_link()
            self.log(f"Username: {self.target_username}")

            self.view_all_stories()

            self.mark_action_sent()
            self.command.update_cmd('state', 'success')

            self.log(f"SUCCESS - Viewed {self.total_stories_viewed} stories")
            self.ig.account.add_cli(f'SUCCESS - Viewed {self.total_stories_viewed} stories', print_only=True)
            self.ig.pause(1500, 2000)

        except LinkIsNotCorrect as e:
            self.log(f"FAILED - LinkIsNotCorrect: {str(e)}")
            self.ig.account.add_cli(f'FAILED - {str(e)}', print_only=True)

            if self.order.status == 'Canceled':
                self.action.status = 'failed'
                self.action.save()
            else:
                self.mark_action_failed_with_charge()

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.log(f"ERROR - {str(e)}")
            self.ig.account.add_cli(f'ERROR - {str(e)}', print_only=True)
            self.action.reset_to_free()

            if self.command:
                self.command.update_cmd('state', 'fail')

    def pick_and_mark_action(self):
        self.action = get_next_action_for_account(self.ig.account, ['view_all_stories'])

        if not self.action:
            raise Exception('There is no view_all_stories order')

        self.order = self.action.order

        self.ig.account.add_cli(f'Order: {self.order.id} | Target: {self.order.target_link}', print_only=True)

        if self.order.status == 'Pending':
            self.order.set_status_to('In progress')

    def parse_and_validate_link(self):
        self.parsed_link = LinkParser.parse(self.order.target_link)

        if self.parsed_link['type'] == LinkParser.TYPE_HIGHLIGHT:
            raise LinkIsNotCorrect("Highlights are not supported")

        if self.parsed_link['username']:
            self.target_username = self.parsed_link['username']
            return

        if LinkParser.needs_username_extraction(self.order.target_link):
            self.target_username = self.extract_username_from_post()
            return

        raise LinkIsNotCorrect("Could not determine username from link")

    def extract_username_from_post(self):
        self.log("Extracting username from post...")
        go_to_page(self.ig, self.order.target_link, 'Post Page')
        self.ig.pause(3000, 4000)

        username = self.click_and_extract_username()

        if username:
            self.log(f"Extracted username: {username}")
            return username

        raise LinkIsNotCorrect("Could not extract username from post")

    def click_and_extract_username(self):
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

    def view_all_stories(self):
        story_url = f"https://www.instagram.com/stories/{self.target_username}/"
        self.log(f"Going to story URL: {story_url}")

        self.remove_response_listener()
        self.setup_response_listener()

        go_to_page(self.ig, story_url, 'Story Page')
        self.ig.pause(3000, 4000)

        current_url = self.ig.page.url
        self.log(f"Current URL after navigation: {current_url}")

        if self.ig.is_visible_by_text("This story is unavailable"):
            self.log("Story unavailable")
            self.remove_response_listener()
            raise Exception("Story unavailable")

        if self.ig.is_visible_by_text("No stories available"):
            self.log("No stories available")
            self.remove_response_listener()
            return

        self.click_view_story_button()
        self.check_story_fail_situations()

        self.log("Waiting for first story confirmation...")
        if not self.wait_for_story_seen(timeout=30):
            self.log("First story NOT confirmed after 30s")
            self.remove_response_listener()
            self.force_exit_story()
            raise Exception("First story not viewed - no confirmation")

        self.log(f"First story confirmed! Watching remaining stories...")
        self.watch_all_stories()

        self.log(f"All stories watched - total: {self.total_stories_viewed}")
        self.remove_response_listener()
        self.force_exit_story()

    def click_view_story_button(self):
        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            attempt += 1

            if '/stories/' in self.ig.page.url and 'View story' not in self.ig.page.content():
                self.log("Already in story view")
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

        return False

    def check_story_fail_situations(self):
        if self.ig.is_visible_by_text("This story is unavailable"):
            self.log("Story is unavailable - failing order")
            self.fail_order_with_full_charge("Story is unavailable")
            raise LinkIsNotCorrect("Story is unavailable")

        if self.ig.is_visible_by_text("Sorry, this page isn't available"):
            self.log("Page not available - failing order")
            self.fail_order_with_full_charge("Story not found")
            raise LinkIsNotCorrect("Story not found")

    def watch_all_stories(self):
        max_stories = 50
        story_count = 1
        last_story_url = None

        while story_count < max_stories:
            self.reset_seen_count()

            current_url = self.ig.page.url

            if '/stories/' not in current_url:
                self.log(f"Exited stories - URL: {current_url}")
                break

            if self.target_username.lower() not in current_url.lower():
                self.log(f"Different user's story - URL: {current_url}")
                break

            if last_story_url and last_story_url == current_url:
                self.log("Same URL as last story - probably last story")
                break

            last_story_url = current_url

            if not self.click_next_story():
                self.log("Could not click next story")
                break

            self.ig.pause(1000, 1500)

            if self.wait_for_story_seen(timeout=30):
                story_count += 1
                self.log(f"Story {story_count} confirmed")
            else:
                self.log(f"Story {story_count} NOT confirmed - stopping")
                break

    def click_next_story(self):
        try:
            viewport = self.ig.page.viewport_size
            if viewport:
                x = int(viewport['width'] * 0.8)
                y = int(viewport['height'] * 0.5)
                self.ig.page.mouse.click(x, y)
                return True
        except:
            pass

        try:
            self.ig.page.keyboard.press('ArrowRight')
            return True
        except:
            pass

        return False

    def force_exit_story(self):
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

    def fail_order_with_full_charge(self, message):
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

                rate = Decimal('0.00005')
                total_charge = Decimal(order.total_count) * rate

                balance = Balance.get(Balance.customer == 'sadeghi')
                balance.balance = balance.balance - total_charge
                balance.save()

        except Exception as e:
            self.log(f"Failed to charge order: {e}")

    def mark_action_sent(self):
        mark_action_completed(self.action)
        deduct_balance('view_all_stories')


    def mark_action_failed_with_charge(self):
        mark_action_failed(self.action)
        deduct_balance('view_all_stories')
