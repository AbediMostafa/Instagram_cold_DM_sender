import json
import random
import re
import time
from urllib.parse import parse_qs, urlparse

from script.extra.helper import go_to_page, tehran_now
from script.extra.exceptions import RetryableError, LinkIsNotCorrect
from script.models.OrderAction import OrderAction
from script.models.Order import Order
from peewee import fn

LIKE_RETRY_ATTEMPTS = 10
LIKE_RETRY_WAIT_MS = (3000, 5000)
LIKE_SCROLL_AMOUNT = 700
COMMENT_POST_RETRY_ATTEMPTS = 3
TYPING_DELAY_MIN_MS = 30
TYPING_DELAY_MAX_MS = 90


class CommentAndReplyPrepareHandler:
    def __init__(self, ig, base_preparer):
        self.ig = ig
        self.base = base_preparer
        self.order = None
        self.first_action = None
        self.original_url = None
        self.normalized_link = None
        self.comment_data = None
        self.comment_id = None
        self.like_data = None
        self.api_type = None

    def prepare(self, order):
        self.order = order

        existing_data = self._get_existing_action_data()

        if existing_data and existing_data.get('comment_posted'):
            # Reply was disabled by executor after retries failed.
            # Navigate to post page and check if comments are actually closed.
            if existing_data.get('reply_disabled'):
                self.ig.account.add_cli('Reply disabled by executor, checking if comments are closed')
                self._validate_link()
                self._normalize_link()
                self._go_to_post_page()

                comment_status = self._check_comment_status()

                if comment_status == 'fully_closed':
                    # Comments completely disabled, can't even like
                    self.ig.account.add_cli('Comments fully closed, canceling order')
                    raise Exception('Comments are fully disabled on this post')

                elif comment_status == 'limited':
                    # Comments limited but likes still work, skip replies only
                    self.ig.account.add_cli('Comments limited, skipping reply actions')
                    self._skip_reply_actions()
                    self._mark_prepared()
                    return

                else:
                    # Comments are open, reply failure was temporary
                    self.ig.account.add_cli('Comments are open, clearing reply_disabled flag')
                    self._clear_reply_disabled(existing_data)
                    self._mark_prepared()
                    return

            if existing_data.get('like_resumed'):
                self.ig.account.add_cli('Resume already attempted once, giving up')
                raise Exception('Like capture failed after resume attempt')

            if not existing_data.get('comment_id') or not existing_data.get('media_id'):
                self.ig.account.add_cli('Comment was posted but essential data (comment_id/media_id) missing, cannot recover')
                raise Exception('Comment capture failed, missing comment_id or media_id')

            self.ig.account.add_cli('Previous attempt posted comment, resuming like-only')
            self._mark_like_resumed(existing_data)
            self._resume_like_only(existing_data)
            return

        self._get_first_action()
        self._validate_link()
        self._normalize_link()
        self._setup_comment_listener()
        self._go_to_post_page()
        self._check_post_errors()
        self._dismiss_popup()
        self._open_comment_box()
        self._post_comment()
        self._verify_comment_posted()

        # Comment was posted successfully. Save flag immediately so if
        # anything below fails, next attempt knows not to post again.
        self._save_comment_posted_flag()

        self._wait_for_comment_capture()

        # Now we have comment_id too, update partial with it
        self._save_partial_capture()

        self._like_own_comment()
        self._wait_for_like_capture()
        self._unlike_own_comment()

        self._finalize_captured_data()

    def _get_existing_action_data(self):
        try:
            fresh = Order.select(Order.action_data).where(Order.id == self.order.id).first()
            if fresh and fresh.action_data:
                return fresh.action_data
        except Exception:
            pass
        return None

    def _mark_like_resumed(self, existing_data):
        """Mark that resume was attempted so next time we fail immediately."""
        existing_data['like_resumed'] = True
        Order.update(
            action_data=existing_data,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _save_comment_posted_flag(self):
        """
        Save minimal flag right after comment is posted.
        Even if comment_id capture fails, next attempt knows comment exists.
        """
        flag = {
            'comment_posted': True,
            'preparer_username': self.ig.account.username,
            'like_captured': False,
        }

        Order.update(
            action_data=flag,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

        self.ig.account.add_cli('Comment posted flag saved')

    def _save_partial_capture(self):
        """
        Save comment data after comment_id is captured.
        If like phase fails, next attempt can skip comment and go to like.
        """
        partial = {
            'comment_posted': True,
            'media_id': self.comment_data['media_id'],
            'comment_id': self.comment_id,
            'preparer_username': self.ig.account.username,
            'api_type': self.api_type,
            'like_captured': False,
        }

        if self.api_type in ('graphql_v1', 'graphql_v2'):
            partial['doc_id'] = self.comment_data.get('doc_id', '')

        Order.update(
            action_data=partial,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

        self.ig.account.add_cli(f'Partial capture saved: comment_id={self.comment_id}')

    def _resume_like_only(self, existing_data):
        """
        Resume from a previous attempt that posted the comment.

        Two sub-cases:
        A) comment_id exists: go to page, find comment, like it
        B) comment_id missing (capture timed out): go to page, find comment,
           like it, extract comment_id from like request variables
        """
        preparer_username = existing_data['preparer_username']
        has_comment_id = bool(existing_data.get('comment_id'))

        if has_comment_id:
            self.comment_data = {
                'media_id': existing_data['media_id'],
                'doc_id': existing_data.get('doc_id', ''),
            }
            self.comment_id = existing_data['comment_id']
            self.api_type = existing_data['api_type']
            self.ig.account.add_cli(f'Resuming with existing comment_id={self.comment_id}')
        else:
            self.ig.account.add_cli('No comment_id from previous attempt, will capture from like request')

        self._get_first_action()
        self._validate_link()
        self._normalize_link()
        self._go_to_post_page()
        self._check_post_errors()
        self._dismiss_popup()

        comment_text = self.first_action.content

        self._setup_like_listener(capture_comment_id=not has_comment_id)

        comment_section = self._find_comment_section()
        if not comment_section:
            self._log('Could not find scrollable comment section, will use page scroll', 'error')

        liked = False
        for attempt in range(1, LIKE_RETRY_ATTEMPTS + 1):
            self.ig.account.add_cli(f'Like attempt {attempt}/{LIKE_RETRY_ATTEMPTS}')

            try:
                if attempt > 1:
                    if comment_section:
                        try:
                            comment_section.evaluate('el => el.scrollBy(0, 500)')
                        except Exception:
                            self.ig.page.mouse.wheel(0, 500)
                    else:
                        self.ig.page.mouse.wheel(0, 500)
                    self.ig.pause(2000, 3000)

                exact_spans = self.ig.page.locator(f'span:text-is("{comment_text}")').all()
                self.ig.account.add_cli(f'Text matches: {len(exact_spans)}')
                if not exact_spans:
                    short_text = comment_text[:30] if len(comment_text) > 30 else comment_text
                    exact_spans = self.ig.page.locator(f'span:has-text("{short_text}")').all()
                    self.ig.account.add_cli(f'Partial matches: {len(exact_spans)}')

                for idx, span in enumerate(exact_spans):
                    try:
                        if not span.is_visible():
                            continue

                        parent = self._find_comment_container(span, preparer_username)
                        if not parent:
                            continue

                        self.ig.account.add_cli(f'Found comment by {preparer_username} at span[{idx}]')

                        unlike_btn = parent.locator('svg[aria-label="Unlike"]').first
                        if unlike_btn.count() > 0 and unlike_btn.is_visible():
                            self.ig.account.add_cli('Comment already liked, unliking first to re-capture')
                            try:
                                unlike_btn.click(timeout=3000)
                                self.ig.pause(2000, 3000)
                            except Exception as e:
                                self._log(f'Unlike failed: {str(e)}', 'error')
                                continue

                        like_svg = parent.locator('svg[aria-label="Like"]').first
                        if not like_svg.count() or not like_svg.is_visible():
                            self._log(f'Like SVG not found/visible at span[{idx}]', 'error')
                            continue

                        clickable = like_svg.locator('xpath=ancestor::div[@role="button"][1]')
                        if clickable.count() > 0:
                            clickable.evaluate('el => el.click()')
                        else:
                            like_svg.evaluate('el => el.closest("[role=button]").click()')

                        self.ig.account.add_cli('Like button clicked')
                        self.ig.pause(3000, 5000)

                        unlike_check = parent.locator('svg[aria-label="Unlike"]').first
                        if unlike_check.count() > 0 and unlike_check.is_visible():
                            self.ig.account.add_cli('Verified: like button changed to unlike')
                            liked = True
                            break

                        self._log(f'Like SVG did not change to Unlike at span[{idx}]', 'error')

                    except Exception as e:
                        self._log(f'Error processing span[{idx}]: {str(e)}', 'exception')
                        continue

                if liked:
                    break

            except Exception as e:
                self._log(f'Like attempt {attempt} error: {str(e)}', 'exception')

            if attempt < LIKE_RETRY_ATTEMPTS:
                self.ig.pause(*LIKE_RETRY_WAIT_MS)

        if not liked:
            raise Exception("Could not find or like the comment after resume attempt")

        self._wait_for_like_capture()

        # If we didn't have comment_id, it should now be captured from like variables
        if not has_comment_id:
            if self.comment_id:
                self.ig.account.add_cli(f'Comment ID recovered from like request: {self.comment_id}')
            else:
                self._log('Could not recover comment_id from like request', 'error')
                raise Exception("Like succeeded but comment_id not captured")

        if not self.comment_data:
            self.comment_data = {'media_id': '', 'doc_id': ''}
            self.api_type = 'graphql_v2'
            if existing_data.get('media_id'):
                self.comment_data['media_id'] = existing_data['media_id']

        self._unlike_own_comment()

        self._finalize_captured_data()

    def _get_first_action(self):
        max_retry_attempts = 3
        retry_wait_seconds = 30
        for attempt in range(1, max_retry_attempts + 1):
            self.first_action = (
                OrderAction.select()
                .where(
                    (OrderAction.order == self.order.id) &
                    (OrderAction.status == 'free') &
                    (OrderAction.content.is_null(False))
                )
                .order_by(OrderAction.id.asc())
                .first()
            )
            if self.first_action:
                if not self.first_action.content or not self.first_action.content.strip():
                    raise Exception('Comment content is empty')
                self.ig.account.add_cli(f'First comment: {self.first_action.content[:50]}...')
                return
            try:
                total = OrderAction.select().where(OrderAction.order == self.order.id).count()
                free = OrderAction.select().where(
                    (OrderAction.order == self.order.id) & (OrderAction.status == 'free')
                ).count()
                free_with_content = OrderAction.select().where(
                    (OrderAction.order == self.order.id) &
                    (OrderAction.status == 'free') &
                    (OrderAction.content.is_null(False))
                ).count()
                statuses = list(
                    OrderAction.select(OrderAction.status, fn.COUNT(OrderAction.id).alias('cnt'))
                    .where(OrderAction.order == self.order.id)
                    .group_by(OrderAction.status)
                    .dicts()
                )
                debug_msg = (
                    f'DEBUG_NO_ACTION: order_id={self.order.id} | attempt={attempt}/{max_retry_attempts} | '
                    f'total_actions={total} | free={free} | free_with_content={free_with_content} | '
                    f'statuses={statuses}'
                )
                self.base._log_to_file(debug_msg, 'debug')
                self.ig.account.add_cli(debug_msg)
                if total == 0 and attempt < max_retry_attempts:
                    self.ig.account.add_cli(
                        f'No actions found for order #{self.order.id}, '
                        f'waiting {retry_wait_seconds}s before retry (attempt {attempt}/{max_retry_attempts})'
                    )
                    time.sleep(retry_wait_seconds)
                    continue
                break
            except Exception as debug_err:
                self.base._log_to_file(f'DEBUG_ERROR: {str(debug_err)}', 'debug')
                break
        raise Exception('No comment action with content found')

    def _validate_link(self):
        parsed = urlparse(self.order.target_link)
        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            raise LinkIsNotCorrect("Invalid link, not an Instagram URL")
        path = parsed.path.strip('/').split('/')
        if len(path) < 2:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")
        valid_first_segment = ["p", "reel", "reels", "tv"]
        if len(path) == 2 and path[0] in valid_first_segment:
            return
        elif len(path) == 3 and path[1] in valid_first_segment:
            return
        else:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

    def _normalize_link(self):
        url = self.order.target_link
        self.normalized_link = re.sub(r'/reels?/', '/p/', url)
        if self.normalized_link != url:
            self.ig.account.add_cli(f'Normalized link: {self.normalized_link}')

    def _setup_comment_listener(self):
        def on_response(response):
            if self.comment_data and self.comment_id:
                return
            try:
                url = response.url
                if '/api/v1/web/comments/' in url and '/add/' in url:
                    self._handle_rest_comment(response)
                    return
                if '/api/graphql' in url or '/graphql/query' in url:
                    self._handle_graphql_comment(response, url)
                    return
            except Exception as e:
                self._log(f'COMMENT_LISTENER error: {str(e)}', 'exception')
        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _handle_rest_comment(self, response):
        url = response.url
        match = re.search(r'/api/v1/web/comments/(\d+)/add/', url)
        if not match:
            self._log(f'REST comment: could not extract media_id from {url}', 'error')
            return
        media_id = match.group(1)
        post_data = response.request.post_data
        if post_data:
            parsed = parse_qs(post_data, keep_blank_values=True)
            if parsed.get('replied_to_comment_id'):
                return
        if not self.comment_data:
            self.comment_data = {'media_id': str(media_id)}
            self.api_type = 'rest'
            self.ig.account.add_cli(f'Comment data captured (REST): media_id={media_id}')
        if not self.comment_id:
            try:
                json_data = response.json()
                comment_id = json_data.get('id')
                status = json_data.get('status')
                if comment_id and status == 'ok':
                    self.comment_id = str(comment_id)
                    self.ig.account.add_cli(f'Comment ID captured: {self.comment_id}')
                else:
                    self._log(f'REST comment unexpected response: id={comment_id}, status={status}', 'error')
            except Exception as e:
                self._log(f'REST comment parse error: {str(e)}', 'exception')

    def _handle_graphql_comment(self, response, url):
        headers = response.request.headers
        friendly_name = headers.get('x-fb-friendly-name', '')
        valid_names = ['usePolarisCommentSubmitMutation', 'PolarisPostCommentInputRevampedMutation']
        if friendly_name not in valid_names:
            return
        post_data = response.request.post_data
        if not post_data:
            return
        parsed = parse_qs(post_data, keep_blank_values=True)
        variables_str = parsed.get('variables', ['{}'])[0]
        try:
            variables = json.loads(variables_str)
        except:
            self._log(f'GQL comment: failed to parse variables: {variables_str[:300]}', 'error')
            return
        data_block = variables.get('data', {})
        request_data_block = variables.get('request_data', {})
        if data_block.get('replied_to_comment_id') or request_data_block.get('replied_to_comment_id'):
            return
        media_id = None
        detected_version = None
        if data_block.get('media_id'):
            media_id = data_block['media_id']
            detected_version = 'graphql_v2'
        elif variables.get('media_id'):
            media_id = variables['media_id']
            detected_version = 'graphql_v1'
        else:
            connections = variables.get('connections', [])
            if connections:
                conn_str = connections[0] if isinstance(connections, list) else str(connections)
                conn_match = re.search(r'media_id[:\\"]+(\d+)', conn_str)
                if conn_match:
                    media_id = conn_match.group(1)
                    detected_version = 'graphql_v2'
        if not media_id:
            self._log(f'GQL comment: no media_id in variables: {list(variables.keys())}', 'error')
            return
        doc_id = parsed.get('doc_id', [''])[0]
        if not self.comment_data:
            self.comment_data = {'media_id': str(media_id), 'doc_id': doc_id}
            self.api_type = detected_version
            self.ig.account.add_cli(f'Comment data captured ({detected_version}): media_id={media_id}, doc_id={doc_id}')
        if not self.comment_id:
            try:
                json_data = response.json()
                pk = None
                xig = json_data.get('data', {}).get('xig_comment_create', {})
                if xig:
                    pk = xig.get('comment_dict', {}).get('pk')
                if not pk:
                    xdt = json_data.get('data', {}).get('xdt_web__comments__media_id__add_queryable', {})
                    if xdt:
                        pk = xdt.get('node', {}).get('pk')
                if pk:
                    self.comment_id = str(pk)
                    self.ig.account.add_cli(f'Comment ID captured: {self.comment_id}')
                else:
                    data_keys = list(json_data.get('data', {}).keys())
                    self._log(f'GQL comment: no pk found, response keys: {data_keys}', 'error')
                    self._log(f'GQL comment response (truncated): {json.dumps(json_data)[:800]}', 'error')
            except Exception as e:
                self._log(f'GQL comment parse error: {str(e)}', 'exception')

    def _setup_like_listener(self, capture_comment_id=False):
        """
        Set up listener for like requests.
        If capture_comment_id=True, also extract comment_id from like variables.
        """
        def on_response(response):
            if self.like_data:
                return
            try:
                url = response.url
                if '/api/v1/web/comments/like/' in url:
                    try:
                        if capture_comment_id and not self.comment_id:
                            cid_match = re.search(r'/comments/like/(\d+)/', url)
                            if cid_match:
                                self.comment_id = cid_match.group(1)
                                self.ig.account.add_cli(f'Comment ID recovered from REST like URL: {self.comment_id}')
                        json_data = response.json()
                        if json_data.get('status') == 'ok':
                            self.like_data = True
                            self.ig.account.add_cli('Like data captured (REST)')
                        else:
                            self._log(f'REST like unexpected status: {json_data.get("status")}', 'error')
                    except Exception as e:
                        self._log(f'REST like parse error: {str(e)}', 'exception')
                    return
                if '/api/graphql' in url or '/graphql/query' in url:
                    headers = response.request.headers
                    friendly_name = headers.get('x-fb-friendly-name', '')
                    like_mutations = ['usePolarisCommentLikeMutation', 'PolarisCommentLikeMutation']
                    is_like_mutation = (
                        friendly_name in like_mutations or
                        ('like' in friendly_name.lower() and 'comment' in friendly_name.lower())
                    )
                    if not is_like_mutation:
                        return
                    post_data = response.request.post_data
                    if not post_data:
                        self._log('GQL like mutation has no POST data', 'error')
                        return
                    parsed = parse_qs(post_data, keep_blank_values=True)
                    doc_id = parsed.get('doc_id', [''])[0]
                    if capture_comment_id and not self.comment_id:
                        try:
                            variables_str = parsed.get('variables', ['{}'])[0]
                            variables = json.loads(variables_str)
                            cid = variables.get('input', {}).get('comment_id')
                            if cid:
                                self.comment_id = str(cid)
                                self.ig.account.add_cli(f'Comment ID recovered from like variables: {self.comment_id}')
                        except Exception:
                            pass
                    if doc_id:
                        self.like_data = doc_id
                        self.ig.account.add_cli(f'Like data captured (GQL): like_doc_id={doc_id}')
                    else:
                        self._log('GQL like mutation: no doc_id in POST data', 'error')
            except Exception as e:
                self._log(f'LIKE_LISTENER error: {str(e)}', 'exception')
        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _go_to_post_page(self):
        go_to_page(self.ig, self.normalized_link, 'Post Page')
        self.ig.pause(10000, 13000)

    def _check_post_errors(self):
        self.original_url = self.ig.page.url
        if '/p/' not in self.original_url and '/reel/' not in self.original_url and '/reels/' not in self.original_url:
            self.ig.account.add_cli(f'Redirected to: {self.original_url}')
            account_issue_paths = ['/accounts/login', '/challenge', '/consent']
            is_account_issue = any(path in self.original_url for path in account_issue_paths)
            if is_account_issue or self.original_url.rstrip('/') in ['https://www.instagram.com', 'https://instagram.com']:
                raise RetryableError(f"Account issue detected (redirected to {self.original_url})")
            raise LinkIsNotCorrect("Account is private or post isn't available (redirected away from post)")
        if self.ig.is_visible_by_text('This account is private') or \
           self.ig.is_visible_by_text('This profile is private'):
            raise LinkIsNotCorrect('Account is private')
        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            raise LinkIsNotCorrect('Comments on this post have been limited')
        if self.ig.is_visible_by_text("Post isn't available") or \
           self.ig.is_visible_by_text("The link may be broken") or \
           self.ig.is_visible_by_text("the profile may have been removed"):
            raise LinkIsNotCorrect("Post isn't available")
        if self.ig.is_visible_by_text("Sorry, this page isn't available") or \
           self.ig.is_visible_by_text("Page is not available") or \
           self.ig.is_visible_by_text("This page isn't available"):
            raise LinkIsNotCorrect("Page is not available")
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise RetryableError("Page load issue - temporary error")
        comment_locator = self.ig.page.locator('svg[aria-label="Comment"]').first
        like_locator = self.ig.page.locator('svg[aria-label="Like"]').first
        if like_locator.is_visible() and not comment_locator.is_visible():
            raise LinkIsNotCorrect("Comment box is not visible")

    def _dismiss_popup(self):
        self.ig.pause(1500, 2500)
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(2000, 3000)
            except Exception:
                pass

    def _open_comment_box(self):
        comment_input = self.ig.page.get_by_placeholder("Add a comment…")
        try:
            if comment_input.count() > 0 and comment_input.is_visible():
                self.ig.account.add_cli('Comment input already visible, no need to click icon')
                return
        except Exception:
            pass
        self.ig.account.add_cli('Comment input not visible, looking for Comment icon...')
        comment_icon_clicked = False
        try:
            icon = self.ig.page.locator("svg[aria-label='Comment']").first
            if icon.count() > 0 and icon.is_visible():
                icon.click(timeout=5000)
                comment_icon_clicked = True
                self.ig.account.add_cli('Clicked Comment icon (svg)')
                self.ig.pause(5000, 7000)
        except Exception:
            pass
        if not comment_icon_clicked:
            try:
                button = self.ig.page.locator("div[role='button']").filter(
                    has=self.ig.page.locator("svg[aria-label='Comment']")
                ).first
                if button.count() > 0 and button.is_visible():
                    button.click(timeout=5000)
                    comment_icon_clicked = True
                    self.ig.account.add_cli('Clicked Comment icon (parent button)')
                    self.ig.pause(5000, 7000)
            except Exception:
                pass
        if not comment_icon_clicked:
            try:
                wrapper = self.ig.page.locator("span div[role='button']:has(svg[aria-label='Comment'])").first
                if wrapper.count() > 0 and wrapper.is_visible():
                    wrapper.click(timeout=5000)
                    comment_icon_clicked = True
                    self.ig.account.add_cli('Clicked Comment icon (span wrapper)')
                    self.ig.pause(5000, 7000)
            except Exception:
                pass
        if not comment_icon_clicked:
            self.ig.account.add_cli('Comment icon not found, will check input in next step')
            return
        self._verify_still_on_same_post()
        self.ig.pause(2000, 3000)

    def _type_like_human(self, locator, text):
        locator.click(timeout=5000)
        self.ig.pause(500, 1000)
        for char in text:
            locator.press_sequentially(char, delay=0)
            delay_ms = random.randint(TYPING_DELAY_MIN_MS, TYPING_DELAY_MAX_MS)
            if char == ' ':
                delay_ms += random.randint(50, 200)
            if random.random() < 0.05:
                delay_ms += random.randint(200, 500)
            self.ig.pause(delay_ms, delay_ms + 20)

    def _post_comment(self):
        comment_text = self.first_action.content
        max_detection_attempts = COMMENT_POST_RETRY_ATTEMPTS
        try:
            comment_input = None
            for attempt in range(1, max_detection_attempts + 1):
                self.ig.account.add_cli(f'Comment input detection attempt {attempt}/{max_detection_attempts}')
                restricted_placeholders = [
                    "Comments on this post have been limited",
                    "Commenting is off",
                    "Comments are turned off",
                    "Comments on this reel have been limited",
                ]
                for restricted_text in restricted_placeholders:
                    try:
                        restricted_input = self.ig.page.get_by_placeholder(restricted_text)
                        if restricted_input.count() > 0 and restricted_input.is_visible():
                            raise LinkIsNotCorrect(f"Comments restricted: {restricted_text}")
                    except LinkIsNotCorrect:
                        raise
                    except Exception:
                        pass
                comment_input_locator = self.ig.page.get_by_placeholder("Add a comment…")
                try:
                    if comment_input_locator.count() > 0 and comment_input_locator.is_visible():
                        comment_input = comment_input_locator
                        self.ig.account.add_cli(f'Comment input found on attempt {attempt}')
                        break
                except Exception:
                    pass
                try:
                    comment_icon = self.ig.page.locator('svg[aria-label="Comment"]').first
                    if comment_icon.count() > 0 and comment_icon.is_visible():
                        self.ig.account.add_cli(f'Attempt {attempt}: icon visible but input not loaded, clicking icon')
                        comment_icon.click(timeout=5000)
                        self.ig.pause(5000, 7000)
                        continue
                except Exception:
                    pass
                if attempt < max_detection_attempts:
                    self.ig.account.add_cli(f'Attempt {attempt}: nothing found, waiting before retry...')
                    self.ig.pause(5000, 7000)
            if not comment_input:
                raise LinkIsNotCorrect("Comments are disabled on this post")
            self.ig.account.add_cli(f'Typing comment: {comment_text[:40]}...')
            self._type_like_human(comment_input, comment_text)
            self.ig.pause(1500, 3000)
            post_button = self.ig.page.get_by_role("button", name="Post", exact=True)
            if post_button.count() == 0 or not post_button.is_visible():
                self.ig.account.add_cli('Post button not visible yet, waiting...')
                self.ig.pause(3000, 4000)
                if post_button.count() == 0 or not post_button.is_visible():
                    raise RetryableError("Post button not found after extended wait")
            post_button.click()
            self.ig.pause(4000, 6000)
            self._verify_still_on_same_post()
        except LinkIsNotCorrect:
            raise
        except RetryableError:
            raise
        except Exception as e:
            raise RetryableError(f"Failed to post comment: {str(e)}")

    def _verify_comment_posted(self):
        self.ig.pause(4000, 6000)
        if self.ig.is_visible_by_text("Couldn't post comment"):
            raise Exception("Couldn't post comment")
        self.ig.account.add_cli("Comment posted successfully")

    def _wait_for_comment_capture(self):
        timeout = 45
        start = time.time()
        last_log = start
        while time.time() - start < timeout:
            if self.comment_data and self.comment_id:
                elapsed = round(time.time() - start, 1)
                self.ig.account.add_cli(
                    f'Comment capture done in {elapsed}s: '
                    f'media_id={self.comment_data.get("media_id")}, '
                    f'comment_id={self.comment_id}, api_type={self.api_type}'
                )
                return True
            now = time.time()
            if now - last_log >= 10:
                self.ig.account.add_cli(
                    f'Waiting for comment capture ({round(now - start, 0)}s) '
                    f'comment_data={self.comment_data is not None}, '
                    f'comment_id={self.comment_id is not None}'
                )
                last_log = now
            time.sleep(0.3)
        missing = []
        if not self.comment_data:
            missing.append('comment_data')
        if not self.comment_id:
            missing.append('comment_id')
        self._log(f'Comment capture timeout after {timeout}s, missing: {", ".join(missing)}', 'error')
        raise TimeoutError(f'Timeout waiting for comment capture. Missing: {", ".join(missing)}')

    def _like_own_comment(self):
        self._setup_like_listener()
        comment_text = self.first_action.content
        username = self.ig.account.username
        self.ig.account.add_cli(f'Looking for our comment to like it (username: {username})')
        comment_section = self._find_comment_section()
        if not comment_section:
            self._log('Could not find scrollable comment section, will use page scroll', 'error')
        for attempt in range(1, LIKE_RETRY_ATTEMPTS + 1):
            self.ig.account.add_cli(f'Like attempt {attempt}/{LIKE_RETRY_ATTEMPTS}')
            try:
                if attempt > 1:
                    if comment_section:
                        try:
                            comment_section.evaluate('el => el.scrollBy(0, 500)')
                        except Exception:
                            self.ig.page.mouse.wheel(0, 500)
                    else:
                        self.ig.page.mouse.wheel(0, 500)
                    self.ig.pause(2000, 3000)
                exact_spans = self.ig.page.locator(f'span:text-is("{comment_text}")').all()
                if not exact_spans:
                    short_text = comment_text[:30] if len(comment_text) > 30 else comment_text
                    exact_spans = self.ig.page.locator(f'span:has-text("{short_text}")').all()
                    self.ig.account.add_cli(f'No exact matches, using partial: {len(exact_spans)} found')
                for idx, span in enumerate(exact_spans):
                    try:
                        if not span.is_visible():
                            continue
                        parent = self._find_comment_container(span, username)
                        if not parent:
                            continue
                        unlike_btn = parent.locator('svg[aria-label="Unlike"]').first
                        if unlike_btn.count() > 0 and unlike_btn.is_visible():
                            self.ig.account.add_cli('Comment already liked')
                            return
                        like_svg = parent.locator('svg[aria-label="Like"]').first
                        if not like_svg.count() or not like_svg.is_visible():
                            self._log(f'Like SVG not found/visible at span[{idx}]', 'error')
                            continue
                        clickable = like_svg.locator('xpath=ancestor::div[@role="button"][1]')
                        if clickable.count() > 0:
                            clickable.evaluate('el => el.click()')
                        else:
                            like_svg.evaluate('el => el.closest("[role=button]").click()')
                        self.ig.account.add_cli('Like button clicked')
                        self.ig.pause(3000, 5000)
                        unlike_check = parent.locator('svg[aria-label="Unlike"]').first
                        if unlike_check.count() > 0 and unlike_check.is_visible():
                            self.ig.account.add_cli('Verified: like button changed to unlike')
                            return
                        self._log(f'Like SVG did not change to Unlike at span[{idx}]', 'error')
                    except Exception as e:
                        self._log(f'Error processing span[{idx}]: {str(e)}', 'exception')
                        continue
            except Exception as e:
                self._log(f'Like attempt {attempt} error: {str(e)}', 'exception')
            if attempt < LIKE_RETRY_ATTEMPTS:
                self.ig.pause(*LIKE_RETRY_WAIT_MS)
        self._log('All like attempts exhausted', 'error')
        raise RetryableError("Could not find and like our own comment")

    def _find_comment_section(self):
        try:
            ul = self.ig.page.locator('ul:has(div[role="button"]:has(svg[aria-label="Like"]))').first
            if ul.count() > 0 and ul.is_visible():
                if ul.evaluate('el => el.scrollHeight > el.clientHeight'):
                    self.ig.account.add_cli('Found scrollable comment section (ul)')
                    return ul
                parent = ul.locator('xpath=ancestor::div[1]')
                if parent.count() > 0:
                    if parent.evaluate('el => el.scrollHeight > el.clientHeight'):
                        self.ig.account.add_cli('Found scrollable comment section (ul parent)')
                        return parent
        except Exception:
            pass
        try:
            handle = self.ig.page.evaluate_handle('''() => {
                const candidates = document.querySelectorAll('div, ul, section');
                for (const el of candidates) {
                    const style = window.getComputedStyle(el);
                    const isScrollable = (
                        el.scrollHeight > el.clientHeight + 50 &&
                        (style.overflowY === 'auto' || style.overflowY === 'scroll' ||
                         style.overflow === 'auto' || style.overflow === 'scroll')
                    );
                    if (isScrollable &&
                        el.querySelector('svg[aria-label="Like"]') &&
                        el.querySelector('a[href]')) {
                        return el;
                    }
                }
                // Fallback: any element with scrollHeight > clientHeight that has comments
                for (const el of candidates) {
                    if (el.scrollHeight > el.clientHeight + 100 &&
                        el.querySelector('svg[aria-label="Like"]') &&
                        el.querySelector('a[href]')) {
                        return el;
                    }
                }
                return null;
            }''')
            if handle:
                element = handle.as_element()
                if element:
                    self.ig.account.add_cli('Found scrollable comment section (JS)')
                    return element
        except Exception:
            pass
        return None

    def _find_comment_container(self, span, username):
        for depth in range(1, 10):
            try:
                ancestor = span.locator(f'xpath=ancestor::div[{depth}]')
                if ancestor.count() == 0:
                    continue
                has_username = (
                    ancestor.locator(f'a[href="/{username}/"]').count() > 0 or
                    ancestor.locator(f'span:text-is("{username}")').count() > 0
                )
                if not has_username:
                    continue
                like_count = ancestor.locator('svg[aria-label="Like"]').count()
                unlike_count = ancestor.locator('svg[aria-label="Unlike"]').count()
                total = like_count + unlike_count
                if total == 0:
                    continue
                if total == 1:
                    return ancestor
            except Exception:
                continue
        return None

    def _wait_for_like_capture(self):
        timeout = 30
        start = time.time()
        last_log = start
        while time.time() - start < timeout:
            if self.like_data:
                elapsed = round(time.time() - start, 1)
                self.ig.account.add_cli(f'Like capture done in {elapsed}s')
                return True
            now = time.time()
            if now - last_log >= 10:
                self.ig.account.add_cli(f'Waiting for like capture ({round(now - start, 0)}s)')
                last_log = now
            time.sleep(0.3)
        self._log('Like capture timeout', 'error')
        raise TimeoutError('Timeout waiting for like data capture')

    def _unlike_own_comment(self):
        try:
            unlike_buttons = self.ig.page.locator('svg[aria-label="Unlike"]').all()
            for idx, btn in enumerate(unlike_buttons):
                try:
                    if btn.is_visible():
                        btn.click(timeout=3000)
                        self.ig.account.add_cli('Unliked our comment')
                        self.ig.pause(1000, 2000)
                        return
                except Exception:
                    continue
        except Exception as e:
            self._log(f'Unlike error (non-critical): {str(e)}', 'error')

    def _finalize_captured_data(self):
        preparer_username = self.ig.account.username

        existing = self._get_existing_action_data()
        if existing and existing.get('preparer_username'):
            preparer_username = existing['preparer_username']

        captured = {
            'comment_posted': True,
            'media_id': self.comment_data['media_id'] if self.comment_data else '',
            'comment_id': self.comment_id,
            'preparer_username': preparer_username,
            'api_type': self.api_type,
            'like_captured': self.like_data is not None and self.like_data != '',
        }
        if self.api_type in ('graphql_v1', 'graphql_v2'):
            captured['doc_id'] = self.comment_data.get('doc_id', '') if self.comment_data else ''
            captured['like_doc_id'] = self.like_data if isinstance(self.like_data, str) else ''
        self.base.captured_data = captured
        self.ig.account.add_cli(f'Final captured data: {captured}')

    def _verify_still_on_same_post(self):
        current_url = self.ig.page.url
        original_id = self._extract_media_id_from_url(self.original_url)
        current_id = self._extract_media_id_from_url(current_url)
        if original_id and current_id and original_id != current_id:
            raise RetryableError(f"Navigated to different post: {current_id} instead of {original_id}")
        if '/reel/' not in current_url and '/p/' not in current_url and '/reels/' not in current_url:
            raise RetryableError("Left post page unexpectedly")

    def _extract_media_id_from_url(self, url):
        match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    def _log(self, message, log_type='info'):
        prefix = f'[CommentAndReply] Order #{self.order.id}' if self.order else '[CommentAndReply]'
        full_message = f'{prefix}: {message}'
        self.ig.account.add_cli(full_message)
        self.base._log_to_file(full_message, log_type)

    def _check_comment_status(self):
        """Check if comments are open, limited, or fully closed.
        Returns 'open', 'limited', or 'fully_closed'."""

        # Check for limited comments (reply blocked but like still works)
        limited_texts = [
            'Comments on this post have been limited',
            'Comments on this reel have been limited',
        ]

        for text in limited_texts:
            try:
                restricted_input = self.ig.page.get_by_placeholder(text)
                if restricted_input.count() > 0 and restricted_input.is_visible():
                    self.ig.account.add_cli(f'Comment status: limited ({text})')
                    return 'limited'
            except Exception:
                pass

        # Check for fully closed comments
        fully_closed_texts = [
            'Commenting is off',
            'Comments are turned off',
        ]

        for text in fully_closed_texts:
            try:
                restricted_input = self.ig.page.get_by_placeholder(text)
                if restricted_input.count() > 0 and restricted_input.is_visible():
                    self.ig.account.add_cli(f'Comment status: fully_closed ({text})')
                    return 'fully_closed'
            except Exception:
                pass

        # If like button is visible but comment button is not, comments are fully closed
        try:
            comment_locator = self.ig.page.locator('svg[aria-label="Comment"]').first
            like_locator = self.ig.page.locator('svg[aria-label="Like"]').first

            if like_locator.is_visible() and not comment_locator.is_visible():
                self.ig.account.add_cli('Comment status: fully_closed (no comment icon)')
                return 'fully_closed'
        except Exception:
            pass

        # No comments yet + no comment input could mean fully closed
        if self.ig.is_visible_by_text('No comments yet'):
            try:
                comment_input = self.ig.page.get_by_placeholder("Add a comment…")
                if comment_input.count() == 0 or not comment_input.is_visible():
                    self.ig.account.add_cli('Comment status: fully_closed (No comments yet, no input)')
                    return 'fully_closed'
            except Exception:
                pass

        return 'open'

    def _clear_reply_disabled(self, existing_data):
        """Remove reply_disabled flag from action_data so executor retries replies."""
        existing_data.pop('reply_disabled', None)

        Order.update(
            action_data=existing_data,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _skip_reply_actions(self):
        """Mark all free reply actions (with content) as skipped and increment
        completed_count for each one so the order can complete normally."""
        reply_actions = list(
            OrderAction.select()
            .where(
                (OrderAction.order == self.order.id) &
                (OrderAction.status == 'free') &
                (OrderAction.content.is_null(False))
            )
        )

        skipped_count = 0
        for action in reply_actions:
            updated = OrderAction.update(
                status='skipped',
                updated_at=tehran_now()
            ).where(
                (OrderAction.id == action.id) &
                (OrderAction.status == 'free')
            ).execute()

            if updated > 0:
                skipped_count += 1

        if skipped_count > 0:
            Order.update(
                completed_count=Order.completed_count + skipped_count
            ).where(
                Order.id == self.order.id
            ).execute()

            self.ig.account.add_cli(f'Skipped {skipped_count} reply actions, incremented completed_count')

            # Check if order is now complete (all replies skipped, no like-only left)
            Order.update(
                status='Completed'
            ).where(
                (Order.id == self.order.id) &
                (Order.completed_count >= Order.total_count) &
                (Order.status != 'Completed')
            ).execute()

    def _mark_prepared(self):
        """Set captured_data so BaseOrderPreparer can continue its normal flow.
        BaseOrderPreparer will call _save_action_data (overwrites with same data,
        harmless) and _mark_first_comment_action_sent (finds no free action with
        content since we just skipped them all, so it does nothing)."""
        self.base.captured_data = self._get_existing_action_data()