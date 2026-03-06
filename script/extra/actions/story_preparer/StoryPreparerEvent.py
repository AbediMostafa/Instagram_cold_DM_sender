import time
import json
import re
import traceback
from datetime import timedelta
from urllib.parse import parse_qs
from script.extra.helper import go_to_page, tehran_now
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.view_story.LinkParser import LinkParser
from script.models.Order import Order
from script.models.OrderAction import OrderAction, ACTION_RATES, deduct_balance
from script.models.Balance import Balance
from script.models.Setting import Setting
from decimal import Decimal


STUCK_TIMEOUT_SECONDS = 120
CAPTURE_TIMEOUT_SECONDS = 30


class StoryPreparerEvent(InstagramMiddleware):
    """Prepares view_story orders by capturing story metadata for API calls"""

    order = None
    parsed_link = None
    target_username = None
    profile_listener = None
    story_listener = None
    profile_data = None
    captured_data = None

    def init(self):
        self._reset_stuck_orders()

        batch_size = int(Setting.get_value('story_prepare_batch_size', 3))

        for i in range(batch_size):
            order = self._claim_next_order()

            if not order:
                if i == 0:
                    self.ig.account.add_cli('No orders to prepare')
                break

            self.order = order
            self.profile_data = None
            self.captured_data = None

            self.ig.account.add_cli(f'Preparing order #{order.id}: {order.target_link}')
            self._process_order()

    def _reset_stuck_orders(self):
        """Reset orders stuck in preparing state"""
        cutoff_time = tehran_now() - timedelta(seconds=STUCK_TIMEOUT_SECONDS)

        Order.update(
            is_prepared=0
        ).where(
            (Order.is_prepared == 1) &
            (Order.updated_at < cutoff_time)
        ).execute()

    def _claim_next_order(self):
        """Find and claim next order using atomic UPDATE"""
        candidate = (
            Order
            .select(Order.id)
            .where(
                (Order.service_type == 'view_story') &
                (Order.is_prepared == 0) &
                (Order.status == 'Pending')
            )
            .order_by(Order.id.asc())
            .first()
        )

        if not candidate:
            return None

        updated = Order.update(
            is_prepared=1,
            updated_at=tehran_now()
        ).where(
            (Order.id == candidate.id) &
            (Order.is_prepared == 0)
        ).execute()

        if updated == 0:
            return None

        return Order.get_by_id(candidate.id)

    def _process_order(self):
        """Process single order"""
        try:
            self._parse_link()

            if self.parsed_link['type'] == LinkParser.TYPE_STORY:
                self._process_direct_story_link()
            else:
                self._process_username_link()

            if not self.captured_data:
                raise Exception('Failed to capture story data')

            self._save_action_data()
            self._create_order_actions()
            self.ig.account.add_cli(f'Order #{self.order.id} prepared successfully')

        except TimeoutError as e:
            self._handle_timeout(str(e))

        except Exception as e:
            self._handle_error(str(e))
            self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')

        finally:
            self._cleanup_listeners()
            self._force_exit_story()

    def _parse_link(self):
        """Parse and validate link"""
        self.parsed_link = LinkParser.parse(self.order.target_link)

        if self.parsed_link['type'] == LinkParser.TYPE_HIGHLIGHT:
            raise Exception('Highlights are not supported')

        if self.parsed_link['type'] == LinkParser.TYPE_STORY:
            self.target_username = self.parsed_link['username']
            return

        if self.parsed_link['username']:
            self.target_username = self.parsed_link['username']
            return

        if LinkParser.needs_username_extraction(self.order.target_link):
            self.target_username = self._extract_username_from_post()
            return

        raise Exception('Could not determine username from link')

    def _process_direct_story_link(self):
        """Process direct story link"""
        self._setup_story_listener()

        go_to_page(self.ig, self.order.target_link, 'Story Page')
        self.ig.pause(4000, 5000)

        self._check_story_errors()
        self._click_view_story()
        self._wait_for_story_data()

    def _process_username_link(self):
        """Process username/profile link"""
        self._setup_profile_listener()

        profile_url = f'https://www.instagram.com/{self.target_username}/'
        go_to_page(self.ig, profile_url, 'Profile Page')
        self.ig.pause(3000, 4000)

        self._check_page_errors()
        self._wait_for_profile_data()
        self._validate_profile_data()

        self._remove_profile_listener()
        self._setup_story_listener()

        story_url = f'https://www.instagram.com/stories/{self.target_username}/'
        go_to_page(self.ig, story_url, 'Story Page')
        self.ig.pause(4000, 5000)

        self._check_story_errors()
        self._click_view_story()
        self._wait_for_story_data()

    def _setup_profile_listener(self):
        """Listen for profile response"""
        self.profile_data = None

        def on_response(response):
            if self.profile_data:
                return

            try:
                if '/graphql' not in response.url:
                    return

                headers = response.request.headers
                friendly_name = headers.get('x-fb-friendly-name', '')

                if friendly_name != 'PolarisProfilePageContentQuery':
                    return

                try:
                    json_data = response.json()
                except:
                    return

                user_data = json_data.get('data', {}).get('user', {})

                if not user_data:
                    self._log_to_file(f'PROFILE_NO_USER: {json.dumps(json_data)[:500]}', 'unknown')
                    return

                self.profile_data = {
                    'is_private': user_data.get('is_private', False),
                    'latest_reel_media': user_data.get('latest_reel_media', 0),
                    'pk': user_data.get('pk', ''),
                    'username': user_data.get('username', ''),
                }

            except Exception as e:
                self._log_to_file(f'PROFILE_LISTENER: {str(e)}\n{traceback.format_exc()}', 'exception')

        self.profile_listener = on_response
        self.ig.page.on('response', self.profile_listener)

    def _remove_profile_listener(self):
        """Remove profile listener"""
        try:
            if self.profile_listener:
                self.ig.page.remove_listener('response', self.profile_listener)
                self.profile_listener = None
        except:
            pass

    def _wait_for_profile_data(self):
        """Wait for profile data"""
        start = time.time()

        while time.time() - start < CAPTURE_TIMEOUT_SECONDS:
            if self.profile_data:
                return
            time.sleep(0.3)

        raise TimeoutError('Timeout waiting for profile data')

    def _validate_profile_data(self):
        """Validate profile data"""
        if not self.profile_data:
            raise Exception('No profile data captured')

        if self.profile_data.get('is_private'):
            raise Exception('Account is private')

        latest_reel = self.profile_data.get('latest_reel_media', 0)
        if not latest_reel or latest_reel == 0:
            raise Exception('User has no active story')

    def _setup_story_listener(self):
        """Listen for story seen request"""
        self.captured_data = None

        def on_response(response):
            if self.captured_data:
                return

            try:
                if '/graphql' not in response.url:
                    return

                post_data = response.request.post_data
                if not post_data:
                    return

                parsed = parse_qs(post_data, keep_blank_values=True)
                fb_api_name = parsed.get('fb_api_req_friendly_name', [''])[0]

                if 'StoriesV3SeenMutation' not in fb_api_name:
                    return

                variables_str = parsed.get('variables', ['{}'])[0]
                doc_id = parsed.get('doc_id', [''])[0]

                try:
                    variables = json.loads(variables_str)
                except:
                    self._log_to_file(f'STORY_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                if 'reelMediaId' not in variables:
                    self._log_to_file(f'STORY_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

                self.captured_data = {
                    'doc_id': doc_id,
                    'reelId': str(variables.get('reelId', '')),
                    'reelMediaId': str(variables.get('reelMediaId', '')),
                    'reelMediaOwnerId': str(variables.get('reelMediaOwnerId', '')),
                    'reelMediaTakenAt': variables.get('reelMediaTakenAt', 0),
                }

                self.ig.account.add_cli(f'Story data captured: {self.captured_data}')

            except Exception as e:
                self._log_to_file(f'STORY_LISTENER: {str(e)}\n{traceback.format_exc()}', 'exception')

        self.story_listener = on_response
        self.ig.page.on('response', self.story_listener)

    def _remove_story_listener(self):
        """Remove story listener"""
        try:
            if self.story_listener:
                self.ig.page.remove_listener('response', self.story_listener)
                self.story_listener = None
        except:
            pass

    def _wait_for_story_data(self):
        """Wait for story data"""
        start = time.time()

        while time.time() - start < CAPTURE_TIMEOUT_SECONDS:
            if self.captured_data:
                return
            time.sleep(0.3)

        raise TimeoutError('Timeout waiting for story data')

    def _click_view_story(self):
        """Click View story button if present"""
        try:
            if not self.ig.is_visible_by_text('View story'):
                return

            selectors = [
                'div[role="button"]:has-text("View story")',
                'button:has-text("View story")',
            ]

            for selector in selectors:
                try:
                    btn = self.ig.page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click(timeout=5000)
                        self.ig.pause(2000, 3000)
                        return
                except:
                    continue

            self.ig.page.get_by_role('button', name=re.compile(r'View story', re.I)).click(timeout=5000)
            self.ig.pause(2000, 3000)

        except Exception as e:
            self.ig.account.add_cli(f'Click view story error: {str(e)}')

    def _check_page_errors(self):
        """Check for page errors"""
        error_texts = [
            "Sorry, this page isn't available",
            "Page is not available",
            "This page isn't available",
            "the page may have been removed",
            "The link you followed may be broken",
        ]

        for text in error_texts:
            if self.ig.is_visible_by_text(text):
                raise Exception(f'Page error: {text}')

    def _check_story_errors(self):
        """Check for story errors"""
        current_url = self.ig.page.url

        if 'show_story_unavailable=1' in current_url:
            raise Exception('Story is unavailable')

        if '/stories/' not in current_url:
            raise Exception('User has no active story')

        error_texts = [
            'This story is unavailable',
            "Sorry, this page isn't available",
            "This page isn't available",
            'No stories available',
            "There's an issue and the page could not be loaded",
        ]

        for text in error_texts:
            if self.ig.is_visible_by_text(text):
                raise Exception(f'Story error: {text}')

        if self.ig.is_visible_by_text('This account is private'):
            raise Exception('Account is private')

    def _extract_username_from_post(self):
        """Extract username from post/reel page"""
        go_to_page(self.ig, self.order.target_link, 'Post Page')
        self.ig.pause(3000, 4000)

        self._check_page_errors()

        selectors = [
            'header a[href^="/"][role="link"]',
            'article header a[href^="/"]',
            'a._a6hd[href^="/"][role="link"]',
        ]

        for selector in selectors:
            try:
                elements = self.ig.page.locator(selector)
                for i in range(min(elements.count(), 5)):
                    element = elements.nth(i)
                    if element.is_visible():
                        href = element.get_attribute('href', timeout=3000)
                        username = self._parse_username_from_href(href)
                        if username:
                            return username
            except:
                continue

        raise Exception('Could not extract username from post')

    def _parse_username_from_href(self, href):
        """Parse username from href"""
        if not href or href == '#':
            return None

        href = href.strip('/').split('/')[0]

        if '?' in href:
            href = href.split('?')[0]

        reserved = ['p', 'reel', 'reels', 'stories', 'explore', 'direct', 'accounts', 'tv', 'tags', 'locations']
        if href.lower() in reserved:
            return None

        if not href or len(href) > 30:
            return None

        if not re.match(r'^[a-zA-Z0-9_.]+$', href):
            return None

        return href

    def _save_action_data(self):
        """Save captured data to order"""
        Order.update(
            is_prepared=2,
            action_data=self.captured_data,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _create_order_actions(self):
        """Create OrderAction records"""
        # First action - preparer's view
        OrderAction.create(
            order_id=self.order.id,
            type='view_story',
            status='sent',
            account=self.ig.account
        )

        Order.update(completed_count=1).where(Order.id == self.order.id).execute()
        deduct_balance('view_story')

        # Remaining actions
        remaining_count = self.order.total_count - 1

        if remaining_count > 0:
            actions = [
                {'order_id': self.order.id, 'type': 'view_story', 'status': 'free'}
                for _ in range(remaining_count)
            ]
            OrderAction.insert_many(actions).execute()

        self.ig.account.add_cli(f'Created 1 sent + {remaining_count} free actions')

    def _handle_timeout(self, message):
        """Handle timeout - reset for retry"""
        self.ig.account.add_cli(f'Order #{self.order.id} timeout: {message}')

        Order.update(
            is_prepared=0,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _handle_error(self, message):
        """Handle error - cancel order and charge"""
        self.ig.account.add_cli(f'Order #{self.order.id} failed: {message}')

        Order.update(
            status='Canceled',
            is_prepared=0,
            description=message,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

        self._charge_full_order()

    def _log_to_file(self, message, log_type='info'):
        """Log to file for debugging Instagram API changes"""
        try:
            import os

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'story_preparer.log')

            order_id = self.order.id if self.order else 'N/A'
            account_id = self.ig.account.id if self.ig.account else 'N/A'
            link = self.order.target_link if self.order else 'N/A'

            log_line = f'[{tehran_now()}] [{log_type.upper()}] order={order_id} | account={account_id} | link={link} | {message}\n'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass

    def _charge_full_order(self):
        """Charge full order amount"""
        rate = ACTION_RATES.get('view_story', Decimal('0.00005'))
        total_charge = Decimal(self.order.total_count) * rate

        Balance.update(
            balance=Balance.balance - total_charge
        ).where(
            Balance.customer == 'sadeghi'
        ).execute()

        self.ig.account.add_cli(f'Charged ${total_charge}')

    def _cleanup_listeners(self):
        """Remove all listeners"""
        self._remove_profile_listener()
        self._remove_story_listener()

    def _force_exit_story(self):
        """Exit story view"""
        try:
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(300, 500)
        except:
            pass