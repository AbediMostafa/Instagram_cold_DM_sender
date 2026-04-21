import json
import traceback
import requests
from script.extra.actions.BaseAction import BaseAction
from script.extra.helper import tehran_now
from script.models.Order import Order
from script.models.OrderAction import (
    OrderAction,
    get_single_action_for_account_prepared,
)
from script.models.Setting import Setting


API_URL = 'https://www.instagram.com/api/graphql'

MAX_RETRY_ATTEMPTS = 3


class BrowserApiCommentAndReplyEvent(BaseAction):
    """
    Execute comment_and_reply actions via direct API calls.

    After the preparer posts the main comment via browser and captures
    GraphQL data (media_id, comment_id, doc_id, like_doc_id, api_type),
    this executor handles two types of remaining actions:

    1. Reply actions (action.content is not null):
       - Like the main comment via API
       - Then post a reply to the main comment via API
       - Reply text is: @{preparer_username} {action.content}

    2. Like-only actions (action.content is null):
       - Only like the main comment via API

    No balance operations for this service type.
    """

    def init(self):
        if not self._validate_graphql_data():
            self.ig.account.add_cli('GraphQL data not available, skipping API comment_and_reply')
            return

        self.session = self._create_proxied_session()
        if not self.session:
            self.ig.account.add_cli('Cannot proceed without proxy')
            return

        batch_size = int(Setting.get_value('comment_batch_size', 2))
        self.processed_order_ids = []

        for i in range(batch_size):
            action = self._get_next_action()

            if not action:
                if i == 0:
                    self.ig.account.add_cli('No prepared comment_and_reply actions available')
                break

            self.action = action
            self.order = action.order
            self.processed_order_ids.append(self.order.id)

            fresh_order = Order.select(Order.status).where(Order.id == self.order.id).first()
            if fresh_order and fresh_order.status == 'Canceled':
                self.ig.account.add_cli(f'Order #{self.order.id} already canceled, skipping')
                self._reset_action()
                continue

            self._load_action_data()

            if not self.action_data:
                self.ig.account.add_cli(f'Order #{self.order.id} has no action_data, skipping')
                self._reset_action()
                continue

            if not self.action_data.get('comment_id') or not self.action_data.get('media_id'):
                self.ig.account.add_cli(f'Order #{self.order.id} missing comment_id or media_id, skipping')
                self._reset_action()
                continue

            self._process_action()
            self.ig.pause(3000, 5000)

        if self.session:
            self.session.close()

    def _create_proxied_session(self):
        """Create a requests session configured with the account's SOCKS5 proxy."""
        session = requests.Session()

        try:
            proxy = self.ig.proxy
            if not proxy:
                self.ig.account.add_cli('[PROXY] No proxy found')
                return None

            session.proxies = proxy.to_requests_proxy()

            if not self._verify_proxy_ip(session, proxy):
                return None

        except Exception as e:
            self.ig.account.add_cli(f'[PROXY] Setup error: {str(e)}')
            return None

        return session

    def _verify_proxy_ip(self, session, proxy):
        """Verify that the proxy's external IP matches the stored real_ip."""
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

            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify skipped')
            return True

        except Exception:
            self.ig.account.add_cli(f'[PROXY] {stored_ip} -> verify skipped')
            return True

    def _validate_graphql_data(self):
        """Check if the required GraphQL data is available from the browser session."""
        if not hasattr(self.ig, 'graphql_data') or not self.ig.graphql_data:
            return False

        if 'headers' not in self.ig.graphql_data or 'payload' not in self.ig.graphql_data:
            return False

        return True

    def _get_next_action(self):
        """Get the next available comment_and_reply action from prepared orders."""
        return get_single_action_for_account_prepared(
            self.ig.account,
            ['comment_and_reply'],
            excluded_order_ids=self.processed_order_ids
        )

    def _load_action_data(self):
        """Load action_data from the order (captured by preparer)."""
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
        """Route to reply+like or like-only based on whether action has content."""
        if self.action.content:
            self._process_reply_action()
        else:
            self._process_like_only_action()

    def _process_reply_action(self):
        """
        Handle a reply action: like the main comment first, then post reply.
        Like goes first so even if reply fails, the like is already done.
        If like fails we still try to reply.
        """
        self.ig.account.add_cli(
            f'Reply action on order #{self.order.id}: {self.action.content[:30]}...'
        )

        try:
            # Step 1: Like the main comment first
            try:
                like_response = self._send_like_request()
                like_success = self._handle_like_response(like_response)

                if not like_success:
                    self.ig.account.add_cli('Like failed, will still try reply')
            except Exception as e:
                self.ig.account.add_cli(f'Like error (non-critical): {str(e)}')

            self.ig.pause(2000, 4000)

            # Step 2: Post reply
            reply_response = self._send_reply_request()
            reply_success = self._handle_reply_response(reply_response)

            if not reply_success:
                return

            self._mark_success()

        except requests.exceptions.RequestException as e:
            self.ig.account.add_cli(f'Network error: {str(e)}')
            self._reset_action()

        except Exception as e:
            self.ig.account.add_cli(f'Error processing reply action: {str(e)}')
            self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')
            self._reset_action()

    def _process_like_only_action(self):
        """
        Handle a like-only action: just like the main comment.
        If like fails, reset action to free so another account can try.
        """
        self.ig.account.add_cli(f'Like-only action on order #{self.order.id}')

        try:
            like_response = self._send_like_request()
            like_success = self._handle_like_response(like_response)

            if like_success:
                self._mark_success()
            else:
                self.ig.account.add_cli('Like-only failed, resetting action to free')
                self._reset_action()

        except requests.exceptions.RequestException as e:
            self.ig.account.add_cli(f'Network error: {str(e)}')
            self._reset_action()

        except Exception as e:
            self.ig.account.add_cli(f'Error processing like-only action: {str(e)}')
            self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')
            self._reset_action()

    # Reply API

    def _send_reply_request(self):
        """Send reply API request. Routes to REST or GraphQL based on api_type."""
        api_type = self.action_data.get('api_type', 'graphql_v2')

        if api_type == 'rest':
            return self._send_reply_rest()
        else:
            return self._send_reply_graphql()

    def _send_reply_graphql(self):
        """Post reply using GraphQL API."""
        headers = self._build_reply_headers()
        payload = self._build_reply_payload()

        return self.session.post(API_URL, headers=headers, data=payload, timeout=30)

    def _send_reply_rest(self):
        """Post reply using REST API."""
        media_id = self.action_data['media_id']
        comment_id = self.action_data['comment_id']
        preparer_username = self.action_data.get('preparer_username', '')
        reply_text = self.action.content

        full_text = f'@{preparer_username} {reply_text}' if preparer_username else reply_text

        url = f'https://www.instagram.com/api/v1/web/comments/{media_id}/add/'

        headers = self.ig.graphql_data['headers'].copy()
        headers.pop('x-fb-friendly-name', None)
        headers.pop('x-root-field-name', None)
        headers['content-type'] = 'application/x-www-form-urlencoded'

        data = {
            'comment_text': full_text,
            'replied_to_comment_id': comment_id,
        }

        return self.session.post(url, headers=headers, data=data, timeout=30)

    def _build_reply_headers(self):
        """Build request headers for the reply API call.
        Reply always uses usePolarisCommentSubmitMutation regardless of
        what api_type the original comment used."""
        headers = self.ig.graphql_data['headers'].copy()
        headers['x-fb-friendly-name'] = 'usePolarisCommentSubmitMutation'
        headers.pop('x-root-field-name', None)
        return headers

    def _build_reply_payload(self):
        """Build the request payload for posting a reply.
        Reply uses the same doc_id captured from the original comment and
        a connections string that references parent_comment_id."""
        payload = self.ig.graphql_data['payload'].copy()

        media_id = self.action_data['media_id']
        comment_id = self.action_data['comment_id']
        doc_id = self.action_data.get('doc_id', '')
        preparer_username = self.action_data.get('preparer_username', '')
        reply_text = self.action.content

        full_text = f'@{preparer_username} {reply_text}' if preparer_username else reply_text

        connections = [
            f'client:root:__PolarisPostComments__xdt_api__v1__media__media_id__comments__'
            f'parent_comment_id__child_comments__connection_connection'
            f'(media_id:"{media_id}",parent_comment_id:"{comment_id}")'
        ]

        # replied_to_comment_id must be integer, not string
        try:
            comment_id_int = int(comment_id)
        except (ValueError, TypeError):
            comment_id_int = comment_id

        variables = {
            'connections': connections,
            'data': {
                'comment_text': full_text,
                'media_id': media_id,
                'replied_to_comment_id': comment_id_int,
            },
        }

        payload['doc_id'] = doc_id
        payload['fb_api_req_friendly_name'] = 'usePolarisCommentSubmitMutation'
        payload['variables'] = json.dumps(variables)

        return payload

    def _handle_reply_response(self, response):
        """Handle the API response for a reply request.
        Returns True if reply was posted successfully, False otherwise."""
        self.ig.account.add_cli(f'Reply response: {response.status_code}')

        if response.status_code == 200:
            try:
                json_data = response.json()
                data = json_data.get('data')
                errors = json_data.get('errors')

                # Any response with errors array goes to execution error handler,
                # even if data is present (e.g. xig_comment_create:null with errors)
                if errors:
                    self._handle_execution_error(json_data)
                    return False

                if data and isinstance(data, dict):
                    xig = data.get('xig_comment_create', {})
                    if xig and xig.get('comment_dict'):
                        self.ig.account.add_cli('Reply posted successfully')
                        return True

                if json_data.get('status') == 'ok' and json_data.get('id'):
                    self.ig.account.add_cli(f'Reply posted successfully (REST): id={json_data["id"]}')
                    return True

                if self._is_client_error(json_data):
                    self._cancel_order('Post or comments not available')
                    return False

                self._log_to_file(f'REPLY_UNKNOWN_200: {json.dumps(json_data)[:1000]}', 'unknown')
                self._reset_action()
                return False

            except json.JSONDecodeError:
                self._log_to_file(f'REPLY_INVALID_JSON: {response.text[:500]}', 'unknown')
                self._reset_action()
                return False

        elif response.status_code == 429:
            self.ig.account.add_cli('Rate limited')
            self._reset_action()
            return False

        elif response.status_code in [401, 403]:
            self.ig.account.add_cli(f'Auth error {response.status_code}')
            self._reset_action()
            return False

        elif response.status_code >= 500:
            self.ig.account.add_cli(f'Server error {response.status_code}')
            self._reset_action()
            return False

        else:
            self._reset_action()
            return False

    # Like API

    def _send_like_request(self):
        """Send like API request. Routes to REST or GraphQL based on api_type."""
        api_type = self.action_data.get('api_type', 'graphql_v2')
        comment_id = self.action_data['comment_id']

        if api_type == 'rest':
            return self._send_like_rest(comment_id)
        else:
            return self._send_like_graphql(comment_id)

    def _send_like_graphql(self, comment_id):
        """Like comment using GraphQL API."""
        headers = self.ig.graphql_data['headers'].copy()
        payload = self.ig.graphql_data['payload'].copy()

        like_doc_id = self.action_data.get('like_doc_id', '')

        if not like_doc_id:
            self.ig.account.add_cli('No like_doc_id available, cannot like')
            return None

        actor_id = payload.get('av', '')

        variables = {
            'input': {
                'actor_id': actor_id,
                'client_mutation_id': '1',
                'comment_id': comment_id,
            },
        }

        headers['x-fb-friendly-name'] = 'usePolarisCommentLikeMutation'
        headers.pop('x-root-field-name', None)
        payload['doc_id'] = like_doc_id
        payload['variables'] = json.dumps(variables)
        payload['fb_api_req_friendly_name'] = 'usePolarisCommentLikeMutation'

        return self.session.post(API_URL, headers=headers, data=payload, timeout=30)

    def _send_like_rest(self, comment_id):
        """Like comment using REST API."""
        url = f'https://www.instagram.com/api/v1/web/comments/like/{comment_id}/'

        headers = self.ig.graphql_data['headers'].copy()
        headers.pop('x-fb-friendly-name', None)
        headers.pop('x-root-field-name', None)
        headers['content-type'] = 'application/x-www-form-urlencoded'

        return self.session.post(url, headers=headers, data={}, timeout=30)

    def _handle_like_response(self, response):
        """Handle the API response for a like request.
        Returns True if like succeeded, False otherwise."""
        if response is None:
            return False

        self.ig.account.add_cli(f'Like response: {response.status_code}')

        if response.status_code == 200:
            try:
                json_data = response.json()

                if json_data.get('data'):
                    self.ig.account.add_cli('Comment liked via API')
                    return True

                if json_data.get('status') == 'ok':
                    self.ig.account.add_cli('Comment liked via REST')
                    return True

                self.ig.account.add_cli(f'Like unexpected response: {json.dumps(json_data)[:200]}')
                self._log_to_file(f'LIKE_UNEXPECTED_200: {json.dumps(json_data)[:500]}', 'error')
                return False

            except json.JSONDecodeError:
                self.ig.account.add_cli('Like: could not parse response')
                self._log_to_file(f'LIKE_INVALID_JSON: {response.text[:500]}', 'error')
                return False

        self.ig.account.add_cli(f'Like HTTP {response.status_code}')
        self._log_to_file(f'LIKE_HTTP_{response.status_code}: {response.text[:500]}', 'error')
        return False

    # Error Handling

    def _handle_execution_error(self, json_data):
        """Handle execution errors (data=null or errors array present).
        Check comments disabled first (no retry needed), then account restriction,
        then retry, then set reply_disabled flag and send to prepare."""
        self.ig.account.add_cli('Execution error detected')
        self._log_to_file(f'EXECUTION_ERROR: {json.dumps(json_data)[:1000]}', 'error')

        # Comments disabled is a definitive signal, no point retrying
        if self._is_comments_disabled(json_data):
            self.ig.account.add_cli('Comments disabled detected from API, sending to prepare')
            self._send_to_prepare_with_reply_disabled()
            return

        if self._is_account_restricted(json_data):
            self.ig.account.add_cli('Account is restricted/blocked, freeing action')
            self._log_to_file(f'ACCOUNT_RESTRICTED: order={self.order.id}', 'error')
            self._reset_action()
            return

        self.ig.account.add_cli('Attempting retries...')
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            self.ig.account.add_cli(f'Retry attempt {attempt}/{MAX_RETRY_ATTEMPTS}')
            self.ig.pause(2000, 3000)

            try:
                response = self._send_reply_request()

                if response.status_code == 200:
                    retry_data = response.json()
                    data = retry_data.get('data')

                    if data and isinstance(data, dict):
                        xig = data.get('xig_comment_create', {})
                        if xig and xig.get('comment_dict'):
                            self.ig.account.add_cli(f'Retry {attempt} succeeded!')
                            self._mark_success()
                            return

                    if retry_data.get('errors'):
                        self._log_to_file(f'RETRY_{attempt}_FAILED: {json.dumps(retry_data)[:500]}', 'error')
                        continue

            except Exception as e:
                self._log_to_file(f'RETRY_{attempt}_EXCEPTION: {str(e)}', 'error')
                continue

        self.ig.account.add_cli(f'All {MAX_RETRY_ATTEMPTS} retries failed, marking reply_disabled')
        self._log_to_file(f'RETRIES_EXHAUSTED: order={self.order.id}', 'error')
        self._send_to_prepare_with_reply_disabled()

    def _is_comments_disabled(self, json_data):
        """Check if the error indicates comments are disabled on this post.
        Instagram returns this in the errors array summary field."""
        errors = json_data.get('errors', [])

        for error in errors:
            summary = str(error.get('summary', '')).lower()
            if 'comments disabled' in summary or 'comments_disabled' in summary:
                return True

        return False

    def _is_account_restricted(self, json_data):
        """Check if the execution error indicates the account is restricted."""
        errors = json_data.get('errors', [])

        for error in errors:
            summary = str(error.get('summary', '')).lower()
            description = str(error.get('description', '')).lower()
            combined = f'{summary} {description}'

            if 'account is restricted' in combined or \
               'temporarily blocked' in combined:
                return True

        return False

    def _is_client_error(self, json_data):
        """Check if the error is the client's fault (post deleted, comments disabled).
        Checks both top-level message field and errors array."""
        error_keywords = [
            'media_not_found', 'post_not_found', 'user_not_found',
            'unavailable', 'not_found', 'does_not_exist',
            'comments_disabled', 'commenting_disabled', 'comments disabled',
        ]

        # Check top-level message
        error_msg = str(json_data.get('message', '')).lower()
        if any(kw in error_msg for kw in error_keywords):
            return True

        # Check errors array
        for error in json_data.get('errors', []):
            summary = str(error.get('summary', '')).lower()
            description = str(error.get('description', '')).lower()
            combined = f'{summary} {description}'
            if any(kw in combined for kw in error_keywords):
                return True

        return False

    # Action Management

    def _mark_success(self):
        """Mark action as completed. No balance deduction for comment_and_reply."""
        Order.update(
            completed_count=Order.completed_count + 1
        ).where(
            Order.id == self.order.id
        ).execute()

        OrderAction.update(
            status='sent',
            updated_at=tehran_now()
        ).where(
            OrderAction.id == self.action.id
        ).execute()

        Order.update(
            status='Completed'
        ).where(
            (Order.id == self.order.id) &
            (Order.completed_count >= Order.total_count) &
            (Order.status != 'Completed')
        ).execute()

        self.ig.account.add_cli(f'SUCCESS order #{self.order.id}')

    def _cancel_order(self, reason):
        """Cancel entire order. No balance operations for comment_and_reply."""
        self.ig.account.add_cli(f'Canceling order #{self.order.id}: {reason}')

        OrderAction.update(
            status='free',
            account=None,
            updated_at=tehran_now()
        ).where(
            (OrderAction.id == self.action.id) &
            (OrderAction.status == 'processing')
        ).execute()

        Order.update(
            status='Canceled',
            description=reason,
            updated_at=tehran_now()
        ).where(
            (Order.id == self.order.id) &
            (Order.status != 'Canceled')
        ).execute()

    def _reset_action(self):
        """Reset action to free status for retry by another account."""
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

    def _send_to_prepare_with_reply_disabled(self):
        """Send order back to prepare with reply_disabled flag.
        Keeps action_data intact so preparer knows comment was already posted.
        Preparer will check if comments are closed and skip reply actions."""
        self.ig.account.add_cli(f'Sending order #{self.order.id} back to prepare (reply_disabled)')

        # Reset current action to free
        OrderAction.update(
            status='free',
            account=None,
            updated_at=tehran_now()
        ).where(
            (OrderAction.id == self.action.id) &
            (OrderAction.status == 'processing')
        ).execute()

        # Add reply_disabled flag to action_data without clearing other fields
        try:
            fresh = Order.select(Order.action_data).where(Order.id == self.order.id).first()
            if fresh and fresh.action_data:
                data = fresh.action_data if isinstance(fresh.action_data, dict) else json.loads(fresh.action_data)
                data['reply_disabled'] = True

                Order.update(
                    is_prepared=0,
                    status='Pending',
                    action_data=data,
                    updated_at=tehran_now()
                ).where(
                    (Order.id == self.order.id) &
                    (Order.status == 'In progress')
                ).execute()

                self.ig.account.add_cli(f'Order #{self.order.id} sent to prepare with reply_disabled')
                self._log_to_file(f'SENT_TO_PREPARE_REPLY_DISABLED: order={self.order.id}', 'info')
            else:
                self.ig.account.add_cli(f'Order #{self.order.id} has no action_data, cannot set flag')
        except Exception as e:
            self.ig.account.add_cli(f'Error setting reply_disabled: {str(e)}')

    def _log_to_file(self, message, log_type='info'):
        """Log message to api_comment_and_reply.log."""
        try:
            import os

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'api_comment_and_reply.log')

            order_id = self.order.id if self.order else 'N/A'
            action_id = self.action.id if self.action else 'N/A'
            account_id = self.ig.account.id if self.ig.account else 'N/A'

            log_line = f'[{tehran_now()}] [{log_type.upper()}] order={order_id} | action={action_id} | account={account_id} | {message}\n'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception:
            pass