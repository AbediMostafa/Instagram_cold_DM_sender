import json
import re
from urllib.parse import parse_qs, urlparse

from script.extra.helper import go_to_page
from script.extra.exceptions import RetryableError, LinkIsNotCorrect
from script.models.OrderAction import OrderAction


class CommentPrepareHandler:
    """Handler for preparing comment orders by posting first comment and capturing API data"""

    def __init__(self, ig, base_preparer):
        self.ig = ig
        self.base = base_preparer
        self.order = None
        self.first_action = None
        self.original_url = None
        self.normalized_link = None

    def prepare(self, order):
        """Main entry point for comment preparation"""
        self.order = order

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
        self.base.wait_for_capture()

    def _get_first_action(self):
        """Get first free action with comment content"""
        self.first_action = (
            OrderAction
            .select()
            .where(
                (OrderAction.order == self.order.id) &
                (OrderAction.status == 'free') &
                (OrderAction.content.is_null(False))
            )
            .order_by(OrderAction.id.asc())
            .first()
        )

        if not self.first_action:
            raise Exception('No comment action with content found')

        if not self.first_action.content or not self.first_action.content.strip():
            raise Exception('Comment content is empty')

        self.ig.account.add_cli(f'First comment: {self.first_action.content[:50]}...')

    def _validate_link(self):
        """Validate post/reel URL"""
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
        """Convert /reel/ and /reels/ to /p/ for consistent behavior"""
        url = self.order.target_link
        self.normalized_link = re.sub(r'/reels?/', '/p/', url)

        if self.normalized_link != url:
            self.ig.account.add_cli(f'Normalized link: {self.normalized_link}')

    def _setup_comment_listener(self):
        """Listen for comment post request to capture media_id and doc_id"""

        def on_response(response):
            if self.base.captured_data:
                return

            try:
                if '/graphql' not in response.url:
                    return

                headers = response.request.headers
                friendly_name = headers.get('x-fb-friendly-name', '')

                if friendly_name != 'PolarisPostCommentInputRevampedMutation':
                    return

                post_data = response.request.post_data
                if not post_data:
                    return

                parsed = parse_qs(post_data, keep_blank_values=True)
                doc_id = parsed.get('doc_id', [''])[0]
                variables_str = parsed.get('variables', ['{}'])[0]

                try:
                    variables = json.loads(variables_str)
                except:
                    self.base._log_to_file(f'COMMENT_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                media_id = variables.get('media_id')

                if not media_id:
                    self.base._log_to_file(f'COMMENT_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

                self.base.captured_data = {
                    'media_id': str(media_id),
                    'doc_id': doc_id,
                }

                self.ig.account.add_cli(f'Comment data captured: {self.base.captured_data}')

            except Exception as e:
                self.base._log_to_file(f'COMMENT_LISTENER: {str(e)}', 'exception')

        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _go_to_post_page(self):
        """Navigate to post page using normalized link"""
        go_to_page(self.ig, self.normalized_link, 'Post Page')
        self.ig.pause(7000, 8000)

    def _check_post_errors(self):
        """Check for post page errors"""
        self.original_url = self.ig.page.url

        # Check if redirected away from post (e.g., private account redirects to profile)
        if '/p/' not in self.original_url and '/reel/' not in self.original_url and '/reels/' not in self.original_url:
            raise LinkIsNotCorrect("Account is private or post isn't available")

        if self.ig.is_visible_by_text('This account is private'):
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
        """Dismiss any popups"""
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(1000, 1500)
            except:
                pass

    def _open_comment_box(self):
        """Open comment box for reels"""
        if 'reels' in self.ig.page.url or 'reel' in self.ig.page.url:
            try:
                self.ig.page.locator("svg[aria-label='Comment']").first.click(timeout=3000)
                self.ig.pause(3000, 3500)
            except:
                try:
                    self.ig.page.locator("div[role='button']").filter(
                        has=self.ig.page.locator("svg[aria-label='Comment']")
                    ).click(timeout=3000)
                    self.ig.pause(3000, 3500)
                except Exception as e:
                    self.ig.account.add_cli(f'Open comment box error: {str(e)}')

            self._verify_still_on_same_post()

    def _verify_still_on_same_post(self):
        """Verify URL hasn't changed (important for reels that can scroll)"""
        current_url = self.ig.page.url

        original_id = self._extract_media_id_from_url(self.original_url)
        current_id = self._extract_media_id_from_url(current_url)

        if original_id and current_id and original_id != current_id:
            raise RetryableError(f"Navigated to different post: {current_id} instead of {original_id}")

        if '/reel/' not in current_url and '/p/' not in current_url and '/reels/' not in current_url:
            raise RetryableError("Left post page unexpectedly")

    def _extract_media_id_from_url(self, url):
        """Extract media shortcode from Instagram URL"""
        match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    def _post_comment(self):
        """Post the first comment"""
        comment_text = self.first_action.content

        try:
            comment_input = self.ig.page.get_by_placeholder("Add a comment…")

            if comment_input.count() == 0:
                raise LinkIsNotCorrect("Comments are disabled on this post")

            if not comment_input.is_visible():
                raise LinkIsNotCorrect("Comment input is not visible - comments may be disabled")

            comment_input.fill(comment_text, timeout=5000)
            self.ig.pause(1500, 2000)

            post_button = self.ig.page.get_by_role("button", name="Post", exact=True)

            if post_button.count() == 0 or not post_button.is_visible():
                raise RetryableError("Post button not found")

            post_button.click()
            self.ig.pause(2000, 3000)

            self._verify_still_on_same_post()

        except LinkIsNotCorrect:
            raise
        except RetryableError:
            raise
        except Exception as e:
            raise RetryableError(f"Failed to post comment: {str(e)}")

    def _verify_comment_posted(self):
        """Verify comment was posted successfully"""
        self.ig.pause(1000, 1500)

        if self.ig.is_visible_by_text("Couldn't post comment"):
            raise Exception("Couldn't post comment")

        self.ig.account.add_cli("Comment posted successfully")