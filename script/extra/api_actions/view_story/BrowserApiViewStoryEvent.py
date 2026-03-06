import time
import json
import random
import requests
from decimal import Decimal
from script.extra.actions.BaseAction import BaseAction
from script.extra.helper import tehran_now
from script.models.Order import Order
from script.models.OrderAction import (
    OrderAction,
    get_single_action_for_account,
    mark_action_completed,
    mark_action_failed,
    deduct_balance,
    ACTION_RATES
)
from script.models.Setting import Setting


API_URL = 'https://www.instagram.com/graphql/query'


class BrowserApiViewStoryEvent(BaseAction):
    """View stories using direct API calls instead of browser interaction"""

    def init(self):
        if not self._validate_graphql_data():
            self.ig.account.add_cli('GraphQL data not available, skipping API view')
            return

        # Create proxied session for this instance
        self.session = self._create_proxied_session()
        if not self.session:
            return

        batch_size = int(Setting.get_value('view_story_batch_size', 10))
        self.processed_order_ids = []

        for i in range(batch_size):
            action = self._get_next_action()

            if not action:
                if i == 0:
                    self.ig.account.add_cli('No prepared view_story actions available')
                break

            self.action = action
            self.order = action.order
            self.processed_order_ids.append(self.order.id)

            self._load_action_data()

            if not self.action_data:
                self.ig.account.add_cli(f'Order #{self.order.id} has no action_data, skipping')
                self._reset_action()
                continue

            self.ig.account.add_cli(f'API viewing story for order #{self.order.id}')
            self._process_action()

            self.ig.pause(300, 600)

        # Close session when done
        if hasattr(self, 'session') and self.session:
            self.session.close()

    def _create_proxied_session(self):
        """
        Create requests session with proxy from ig (BasePlaywright).
        Uses the same proxy that is set on AdsPower profile.
        """
        session = requests.Session()

        try:
            proxy = self.ig.proxy
            if not proxy:
                self.ig.account.add_cli('[PROXY] No proxy found')
                return session

            session.proxies = proxy.to_requests_proxy()
            self._verify_proxy_ip(session, proxy)

        except Exception as e:
            self.ig.account.add_cli(f'[PROXY] Setup error: {str(e)}')

        return session

    def _verify_proxy_ip(self, session, proxy):
        """
        Verify that session is using the correct proxy by checking external IP.
        """
        stored_ip = proxy.real_ip or 'unknown'

        try:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            if response.status_code == 200:
                current_ip = response.json().get('ip', 'unknown')

                if current_ip == stored_ip:
                    self.ig.account.add_cli(f'[PROXY] {current_ip} -> OK')
                else:
                    self.ig.account.add_cli(f'[PROXY] {current_ip} vs {stored_ip} -> MISMATCH')
            else:
                self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify failed (status {response.status_code})')

        except Exception:
            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify failed (blocked)')

    def _validate_graphql_data(self):
        """Check if graphql_data is available"""
        if not hasattr(self.ig, 'graphql_data') or not self.ig.graphql_data:
            return False

        if 'headers' not in self.ig.graphql_data or 'payload' not in self.ig.graphql_data:
            return False

        return True

    def _get_next_action(self):
        """Get next action from prepared orders only"""
        return get_single_action_for_account_prepared(
            self.ig.account,
            ['view_story'],
            excluded_order_ids=self.processed_order_ids
        )

    def _load_action_data(self):
        """Load action_data from order"""
        self.action_data = None

        try:
            fresh_order = Order.select(Order.action_data).where(Order.id == self.order.id).first()

            if fresh_order and fresh_order.action_data:
                if isinstance(fresh_order.action_data, str):
                    self.action_data = json.loads(fresh_order.action_data)
                else:
                    self.action_data = fresh_order.action_data
        except Exception as e:
            self.ig.account.add_cli(f'Error loading action_data: {str(e)}')

    def _process_action(self):
        """Process single action"""
        try:
            response = self._send_api_request()
            self._handle_response(response)

        except requests.exceptions.RequestException as e:
            self.ig.account.add_cli(f'Network error: {str(e)}')
            self._reset_action()

        except Exception as e:
            self.ig.account.add_cli(f'Error processing action: {str(e)}')
            self._reset_action()

    def _send_api_request(self):
        """Send story view API request through proxied session"""
        headers = self._build_headers()
        payload = self._build_payload()

        response = self.session.post(
            API_URL,
            headers=headers,
            data=payload,
            timeout=30
        )

        return response

    def _build_headers(self):
        """Build request headers"""
        headers = self.ig.graphql_data['headers'].copy()

        headers['x-fb-friendly-name'] = 'PolarisStoriesV3SeenMutation'
        headers['x-root-field-name'] = 'xdt_api__v1__stories__reel__seen'

        return headers

    def _build_payload(self):
        """Build request payload"""
        payload = self.ig.graphql_data['payload'].copy()

        view_seen_at = int(time.time()) - random.randint(5, 30)

        variables = {
            'reelId': self.action_data['reelId'],
            'reelMediaId': self.action_data['reelMediaId'],
            'reelMediaOwnerId': self.action_data['reelMediaOwnerId'],
            'reelMediaTakenAt': self.action_data['reelMediaTakenAt'],
            'viewSeenAt': view_seen_at
        }

        payload['doc_id'] = self.action_data.get('doc_id')
        payload['fb_api_req_friendly_name'] = 'PolarisStoriesV3SeenMutation'
        payload['__crn'] = 'comet.igweb.PolarisStoriesV3Route'
        payload['variables'] = json.dumps(variables)

        return payload

    def _handle_response(self, response):
        """Handle API response"""
        self.ig.account.add_cli(f'API response status: {response.status_code}')

        if response.status_code == 200:
            try:
                json_data = response.json()

                if json_data.get('status') == 'ok' or 'data' in json_data:
                    self._mark_success()
                    return

                error_msg = json_data.get('message', 'Unknown API error')
                self.ig.account.add_cli(f'API error: {error_msg}')

                if self._is_client_error(json_data):
                    self._mark_failed()
                else:
                    self._reset_action()

            except json.JSONDecodeError:
                self.ig.account.add_cli('Invalid JSON response')
                self._reset_action()

        elif response.status_code == 429:
            self.ig.account.add_cli('Rate limited')
            self._reset_action()

        elif response.status_code in [401, 403]:
            self.ig.account.add_cli('Auth error - session may be invalid')
            self._reset_action()

        elif response.status_code >= 500:
            self.ig.account.add_cli('Server error')
            self._reset_action()

        else:
            self.ig.account.add_cli(f'HTTP error: {response.status_code}')
            self._reset_action()

    def _is_client_error(self, json_data):
        """Check if error is client's fault (invalid link, expired, etc)"""
        error_messages = [
            'story_not_found',
            'media_not_found',
            'user_not_found',
            'expired',
            'unavailable',
        ]

        error_msg = str(json_data.get('message', '')).lower()

        for err in error_messages:
            if err in error_msg:
                return True

        return False

    def _mark_success(self):
        """Mark action as successful"""
        mark_action_completed(self.action)
        deduct_balance('view_story')
#         self._log_to_file('Story viewed successfully', 'success')
        self.ig.account.add_cli(f'SUCCESS - Story viewed via API for order #{self.order.id}')

    def _mark_failed(self):
        """Mark action as failed (client error)"""
        mark_action_failed(self.action)
        deduct_balance('view_story')
        self._log_to_file('Client error - marked as failed', 'error')
        self.ig.account.add_cli(f'FAILED - Client error for order #{self.order.id}')

    def _reset_action(self):
        """Reset action to free (our error, let another account try)"""
        try:
            OrderAction.update(
                status='free',
                account=None,
                updated_at=tehran_now()
            ).where(
                (OrderAction.id == self.action.id) &
                (OrderAction.status == 'processing')
            ).execute()

            self._log_to_file('Reset to free for retry', 'retry')
            self.ig.account.add_cli(f'Reset action to free for order #{self.order.id}')
        except Exception as e:
            self.ig.account.add_cli(f'Error resetting action: {str(e)}')

    def _log_to_file(self, message, log_type='info'):
        """Log to file"""
        try:
            import os

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'api_view_story.log')

            order_id = self.order.id if self.order else 'N/A'
            action_id = self.action.id if self.action else 'N/A'

            log_line = f'[{tehran_now()}] [{log_type.upper()}] order_id={order_id} | action_id={action_id} | {message}\n'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception as e:
            self.ig.account.add_cli(f'Failed to write log: {str(e)}')


def get_single_action_for_account_prepared(account, action_types, excluded_order_ids=None):
    """
    Get a single action for prepared orders only (is_prepared=2).
    Uses atomic UPDATE to avoid race conditions.
    """
    if excluded_order_ids is None:
        excluded_order_ids = []

    worked_order_ids = list(
        OrderAction
        .select(OrderAction.order)
        .where(OrderAction.account == account)
        .distinct()
        .tuples()
    )
    worked_order_ids = [x[0] for x in worked_order_ids]

    all_excluded = set(worked_order_ids + excluded_order_ids)

    random_offset = random.randint(0, 20)

    query = (
        OrderAction
        .select(OrderAction.id, OrderAction.order)
        .join(Order)
        .where(
            (OrderAction.type.in_(action_types)) &
            (Order.status.in_(['Pending', 'In progress'])) &
            (Order.is_prepared == 2) &
            (OrderAction.status == 'free')
        )
        .order_by(Order.id, OrderAction.id)
        .offset(random_offset)
        .limit(10)
    )

    if all_excluded:
        query = query.where(~(OrderAction.order.in_(all_excluded)))

    candidates = list(query)

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            OrderAction
            .update(
                status='processing',
                account=account,
                updated_at=tehran_now()
            )
            .where(
                (OrderAction.id == candidate.id) &
                (OrderAction.status == 'free')
            )
            .execute()
        )

        if updated > 0:
            Order.update(
                status='In progress'
            ).where(
                (Order.id == candidate.order_id) &
                (Order.status == 'Pending')
            ).execute()

            return OrderAction.get_by_id(candidate.id)

    return None