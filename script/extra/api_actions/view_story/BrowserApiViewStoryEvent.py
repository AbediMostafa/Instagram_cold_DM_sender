import time
import json
import random
import traceback
import requests
from script.extra.actions.BaseAction import BaseAction
from script.extra.helper import tehran_now
from script.models.Order import Order
from script.models.OrderAction import (
    OrderAction,
    mark_action_completed,
    get_single_action_for_account_prepared,
)
from script.models.Balance import Balance
from script.models.Setting import Setting


API_URL = 'https://www.instagram.com/graphql/query'

# Maximum number of retry attempts for execution errors
# After this many failures, order goes back to prepare queue
MAX_RETRY_ATTEMPTS = 3


class BrowserApiViewStoryEvent(BaseAction):
    """
    View stories using direct API calls instead of browser interaction.

    This class handles the execution phase of view_story orders. It:
    1. Gets prepared orders (is_prepared=2) with action_data containing reelId, reelMediaId, etc.
    2. Sends GraphQL API requests to mark stories as seen
    3. Handles success/failure scenarios appropriately

    Error handling strategy:
    - Success: Mark action as sent, deduct balance
    - Client error (story expired, user not found): Cancel entire order, charge remaining
    - Execution error with retries: Retry up to MAX_RETRY_ATTEMPTS times
    - Execution error after retries: Send order back to prepare queue for verification
    - Network/server error: Reset action to free for another account to try
    """

    def init(self):
        """
        Main entry point for processing view_story actions.

        Flow:
        1. Validate GraphQL data is available
        2. Create proxied session with IP verification
        3. Process batch of actions based on batch_size setting
        """
        # Validate that we have the necessary GraphQL data from browser session
        if not self._validate_graphql_data():
            self.ig.account.add_cli('GraphQL data not available, skipping API view')
            return

        # Create a requests session configured with the account's proxy
        self.session = self._create_proxied_session()
        if not self.session:
            self.ig.account.add_cli('Cannot proceed without proxy')
            return

        # Get batch size from settings (how many actions to process per run)
        batch_size = int(Setting.get_value('view_story_batch_size', 10))
        self.processed_order_ids = []

        # Process actions in batch
        for i in range(batch_size):
            action = self._get_next_action()

            if not action:
                if i == 0:
                    self.ig.account.add_cli('No prepared view_story actions available')
                break

            self.action = action
            self.order = action.order
            self.processed_order_ids.append(self.order.id)

            # Check if order was already canceled by another thread
            fresh_order = Order.select(Order.status).where(Order.id == self.order.id).first()
            if fresh_order and fresh_order.status == 'Canceled':
                self.ig.account.add_cli(f'Order #{self.order.id} already canceled, skipping')
                self._reset_action()
                continue

            # Load the action_data captured during prepare phase
            self._load_action_data()

            if not self.action_data:
                self.ig.account.add_cli(f'Order #{self.order.id} has no action_data, skipping')
                self._reset_action()
                continue

            self.ig.account.add_cli(f'API viewing story for order #{self.order.id}')
            self._process_action()

            # Pause between actions to avoid rate limiting
            self.ig.pause(3000, 5000)

        # Clean up session when done
        if self.session:
            self.session.close()

    def _create_proxied_session(self):
        """
        Create a requests session configured with the account's SOCKS5 proxy.

        Also verifies that the proxy IP matches the expected IP to ensure
        requests go through the correct proxy.

        Returns:
            requests.Session or None if proxy unavailable or IP mismatch
        """
        session = requests.Session()

        try:
            proxy = self.ig.proxy
            if not proxy:
                self.ig.account.add_cli('[PROXY] No proxy found')
                return None

            # Configure session to use SOCKS5 proxy
            session.proxies = proxy.to_requests_proxy()

            # Verify the proxy IP matches what we expect
            if not self._verify_proxy_ip(session, proxy):
                return None

        except Exception as e:
            self.ig.account.add_cli(f'[PROXY] Setup error: {str(e)}')
            return None

        return session

    def _verify_proxy_ip(self, session, proxy):
        """
        Verify that the proxy's external IP matches the stored real_ip.

        This prevents requests from going through the wrong proxy or
        being sent without a proxy at all.

        Returns:
            True if IP matches or verification was skipped
            False if IP mismatch detected (requests should not proceed)
        """
        stored_ip = proxy.real_ip or 'unknown'

        try:
            response = session.get('https://api.ipify.org?format=json', timeout=10)
            if response.status_code == 200:
                current_ip = response.json().get('ip', 'unknown')

                if current_ip == stored_ip:
                    self.ig.account.add_cli(f'[PROXY] {current_ip} -> OK')
                    return True
                else:
                    self.ig.account.add_cli(f'[PROXY] {current_ip} vs {stored_ip} -> MISMATCH')
                    return False

            # If we can't verify, allow to proceed (verification skipped)
            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify skipped')
            return True

        except Exception:
            # Network error during verification - allow to proceed
            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify skipped')
            return True

    def _validate_graphql_data(self):
        """
        Check if the required GraphQL data is available from the browser session.

        The graphql_data contains headers (cookies, tokens) and base payload
        captured from the browser, which we need to make authenticated API calls.
        """
        if not hasattr(self.ig, 'graphql_data') or not self.ig.graphql_data:
            return False

        if 'headers' not in self.ig.graphql_data or 'payload' not in self.ig.graphql_data:
            return False

        return True

    def _get_next_action(self):
        """
        Get the next available action from prepared orders.

        Only considers orders with is_prepared=2 (fully prepared with action_data).
        Uses atomic UPDATE to prevent race conditions with other threads.
        """
        return get_single_action_for_account_prepared(
            self.ig.account,
            ['view_story'],
            excluded_order_ids=self.processed_order_ids
        )

    def _load_action_data(self):
        """
        Load action_data from the order.

        action_data contains reelId, reelMediaId, reelMediaOwnerId, reelMediaTakenAt, and doc_id
        captured during the prepare phase when the first story was viewed via browser.
        """
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
        """
        Process a single view_story action.

        Sends the API request and handles the response appropriately.
        Network errors result in action being reset to free for retry.
        """
        try:
            response = self._send_api_request()
            self._handle_response(response)

        except requests.exceptions.RequestException as e:
            # Network error - reset action for another account to try
            self.ig.account.add_cli(f'Network error: {str(e)}')
            self._reset_action()

        except Exception as e:
            # Unexpected error - log and reset action
            self.ig.account.add_cli(f'Error processing action: {str(e)}')
            self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')
            self._reset_action()

    def _send_api_request(self):
        """
        Send the GraphQL API request to mark story as seen.

        Returns:
            requests.Response object
        """
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
        """
        Build request headers for the story view API call.

        Starts with base headers from graphql_data and adds
        story-specific headers.
        """
        headers = self.ig.graphql_data['headers'].copy()
        headers['x-fb-friendly-name'] = 'PolarisStoriesV3SeenMutation'
        headers['x-root-field-name'] = 'xdt_api__v1__stories__reel__seen'
        return headers

    def _build_payload(self):
        """
        Build the request payload for marking story as seen.

        Uses story data from action_data and generates a realistic viewSeenAt timestamp.
        """
        payload = self.ig.graphql_data['payload'].copy()

        # Generate a realistic "when user saw the story" timestamp
        # Slightly in the past to simulate natural viewing behavior
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
        """
        Handle the API response and take appropriate action.

        Response scenarios:
        - 200 with data: Success, story view was recorded
        - 200 with data=null and errors: Execution error, retry or send to prepare
        - 200 with client error message: Cancel order (client's fault)
        - 429: Rate limited, reset action for retry
        - 401/403: Auth error, reset action
        - 5xx: Server error, reset action
        """
        self.ig.account.add_cli(f'API response: {response.status_code}')

        if response.status_code == 200:
            try:
                json_data = response.json()
                data = json_data.get('data')

                # Check for execution error: data is null with errors array
                # This could be temporary (Instagram issue) or permanent (story expired)
                if data is None and json_data.get('errors'):
                    self._handle_execution_error(json_data)
                    return

                # Success: story view was recorded
                if json_data.get('status') == 'ok' or data:
                    self._mark_success()
                    return

                # Check for known client errors in message field
                if self._is_client_error(json_data):
                    self._cancel_order('Story is not available')
                    return

                # Unknown response format - log for analysis and reset action
                self._log_to_file(f'UNKNOWN_200: {json.dumps(json_data)[:1000]}', 'unknown')
                self._reset_action()

            except json.JSONDecodeError:
                self._log_to_file(f'INVALID_JSON: {response.text[:500]}', 'unknown')
                self._reset_action()

        elif response.status_code == 429:
            # Rate limited - reset action for another account to try later
            self.ig.account.add_cli('Rate limited')
            self._reset_action()

        elif response.status_code in [401, 403]:
            # Authentication error - reset action
            self._log_to_file(f'AUTH_ERROR_{response.status_code}: {response.text[:500]}', 'unknown')
            self._reset_action()

        elif response.status_code >= 500:
            # Server error - reset action for retry
            self._reset_action()

        else:
            # Other error - reset action
            self._log_to_file(f'HTTP_{response.status_code}: {response.text[:500]}', 'unknown')
            self._reset_action()

    def _handle_execution_error(self, json_data):
        """
        Handle execution errors (data=null with errors array).

        These errors are ambiguous - could be:
        - Temporary Instagram issue (should retry)
        - Story expired or user went private (should cancel)
        - Account is restricted/blocked (should skip, let other accounts try)

        Strategy:
        1. Check if error is account-level (restricted/blocked) - if so, reset immediately
        2. Retry up to MAX_RETRY_ATTEMPTS times with this same account
        3. If all retries fail, send order back to prepare queue
        4. Prepare will verify if story is still available via browser
        """
        self.ig.account.add_cli(f'Execution error detected')
        self._log_to_file(f'EXECUTION_ERROR: {json.dumps(json_data)[:1000]}', 'error')

        # Check if the error is account-level (restricted/blocked)
        # Retrying with the same account is pointless in this case -
        # just free the action so other accounts can pick it up
        if self._is_account_restricted(json_data):
            self.ig.account.add_cli('Account is restricted/blocked, skipping retries and freeing action')
            self._log_to_file(f'ACCOUNT_RESTRICTED: order={self.order.id}', 'error')
            self._reset_action()
            return

        # Retry loop - try MAX_RETRY_ATTEMPTS times
        self.ig.account.add_cli(f'Attempting retries...')
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            self.ig.account.add_cli(f'Retry attempt {attempt}/{MAX_RETRY_ATTEMPTS}')
            self.ig.pause(2000, 3000)

            try:
                response = self._send_api_request()

                if response.status_code == 200:
                    retry_data = response.json()
                    data = retry_data.get('data')

                    # Success on retry
                    if retry_data.get('status') == 'ok' or data:
                        self.ig.account.add_cli(f'Retry {attempt} succeeded!')
                        self._mark_success()
                        return

                    # Still getting execution error, continue retry loop
                    if data is None and retry_data.get('errors'):
                        self._log_to_file(f'RETRY_{attempt}_FAILED: {json.dumps(retry_data)[:500]}', 'error')
                        continue

            except Exception as e:
                self._log_to_file(f'RETRY_{attempt}_EXCEPTION: {str(e)}', 'error')
                continue

        # All retries exhausted - send order back to prepare queue
        self.ig.account.add_cli(f'All {MAX_RETRY_ATTEMPTS} retries failed, sending order back to prepare')
        self._log_to_file(f'RETRIES_EXHAUSTED: order={self.order.id} sent back to prepare', 'error')
        self._send_to_prepare()

    def _is_account_restricted(self, json_data):
        """
        Check if the execution error indicates the account is restricted or blocked.

        These errors mean the problem is with the account, not the story.
        Retrying with the same account will always fail, so we should free
        the action for other accounts to handle.

        Args:
            json_data: Parsed JSON response from Instagram API

        Returns:
            True if error is account-level (restricted/blocked)
            False if error is something else (should proceed with retries)
        """
        errors = json_data.get('errors', [])

        for error in errors:
            summary = str(error.get('summary', '')).lower()
            description = str(error.get('description', '')).lower()

            combined = f'{summary} {description}'

            if 'account is restricted' in combined or \
               'temporarily blocked' in combined:
                return True

        return False

    def _send_to_prepare(self):
        """
        Send order back to prepare queue for re-verification.

        This is called when we get persistent execution errors that might indicate
        the story expired or user went private. The prepare phase will verify via
        browser whether the story is still accessible.

        Actions:
        - Reset current action to free
        - Set order status to Pending
        - Set is_prepared to 0 (needs re-preparation)
        - Do NOT change completed_count or deduct balance
        """
        self.ig.account.add_cli(f'Sending order #{self.order.id} back to prepare queue')

        # Reset current action to free
        OrderAction.update(
            status='free',
            account=None,
            updated_at=tehran_now()
        ).where(
            (OrderAction.id == self.action.id) &
            (OrderAction.status == 'processing')
        ).execute()

        # Send order back to prepare queue
        # Only update if order is still In progress (another thread might have completed it)
        updated = Order.update(
            status='Pending',
            is_prepared=0,
            updated_at=tehran_now()
        ).where(
            (Order.id == self.order.id) &
            (Order.status == 'In progress')
        ).execute()

        if updated > 0:
            self.ig.account.add_cli(f'Order #{self.order.id} sent to prepare queue')
            self._log_to_file(f'SENT_TO_PREPARE: order={self.order.id}', 'info')
        else:
            self.ig.account.add_cli(f'Order #{self.order.id} status already changed, skipping')

    def _is_client_error(self, json_data):
        """
        Check if the error is the client's fault (story expired, etc.)

        These errors mean the order should be canceled and client charged.
        """
        error_keywords = [
            'story_not_found',
            'media_not_found',
            'user_not_found',
            'expired',
            'unavailable',
        ]

        error_msg = str(json_data.get('message', '')).lower()
        return any(kw in error_msg for kw in error_keywords)

    def _mark_success(self):
        """
        Mark action as successfully completed.

        This increments completed_count, marks action as sent,
        and deducts balance (all handled by mark_action_completed).
        """
        mark_action_completed(self.action)
        self.ig.account.add_cli(f'SUCCESS order #{self.order.id}')

    def _cancel_order(self, reason):
        """
        Cancel entire order due to client error.

        Called when we're certain the order cannot be completed
        (e.g., story expired, user went private).

        Actions:
        - Reset current action to free
        - Cancel order with reason
        - Deduct balance for all remaining actions (client pays for their mistake)
        """
        self.ig.account.add_cli(f'Canceling order #{self.order.id}: {reason}')

        # Reset current action to free first
        OrderAction.update(
            status='free',
            account=None,
            updated_at=tehran_now()
        ).where(
            (OrderAction.id == self.action.id) &
            (OrderAction.status == 'processing')
        ).execute()

        # Atomically cancel order (only if not already canceled by another thread)
        updated = Order.update(
            status='Canceled',
            description=reason,
            updated_at=tehran_now()
        ).where(
            (Order.id == self.order.id) &
            (Order.status != 'Canceled')
        ).execute()

        if updated > 0:
            # Only first thread to cancel deducts balance for remaining actions
            fresh_order = Order.select(Order.total_count, Order.completed_count).where(Order.id == self.order.id).first()
            if fresh_order:
                remaining = fresh_order.total_count - fresh_order.completed_count
                if remaining > 0:
                    total_charge = Balance.deduct_for_actions('view_story', remaining)
                    self.ig.account.add_cli(f'Charged ${total_charge} for {remaining} remaining actions')

    def _reset_action(self):
        """
        Reset action to free status for retry by another account.

        Called when we encounter temporary errors (network, rate limit, etc.)
        that might succeed with a different account or at a different time.
        No balance is deducted.
        """
        try:
            OrderAction.update(
                status='free',
                account=None,
                updated_at=tehran_now()
            ).where(
                (OrderAction.id == self.action.id) &
                (OrderAction.status == 'processing')
            ).execute()
        except Exception as e:
            self.ig.account.add_cli(f'Reset error: {str(e)}')

    def _log_to_file(self, message, log_type='info'):
        """
        Log message to file for debugging and analysis.

        Log files help track Instagram API changes and debug issues.
        """
        try:
            import os

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'api_view_story.log')

            order_id = self.order.id if self.order else 'N/A'
            action_id = self.action.id if self.action else 'N/A'
            account_id = self.ig.account.id if self.ig.account else 'N/A'

            log_line = f'[{tehran_now()}] [{log_type.upper()}] order={order_id} | action={action_id} | account={account_id} | {message}\n'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass