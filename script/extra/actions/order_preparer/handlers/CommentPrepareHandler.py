import json
import re
from urllib.parse import parse_qs, urlparse

from script.extra.helper import go_to_page
from script.extra.exceptions import RetryableError, LinkIsNotCorrect
from script.models.OrderAction import OrderAction


class CommentPrepareHandler:
    """
    Handler for preparing comment orders by posting the first comment via browser.

    Unlike view_story and save_post, comment orders have their OrderAction records
    created by Laravel (OrderController) with the comment content already set.
    This handler posts the first comment via browser automation and captures
    the GraphQL request data for subsequent API-based comments.

    The captured data (media_id, doc_id) is stored in order.action_data and used
    by BrowserApiCommentEvent to post remaining comments via direct API calls.

    Flow:
    1. Get first OrderAction with comment content
    2. Validate and normalize the post URL (convert /reel/ to /p/)
    3. Set up network listener to capture comment request
    4. Navigate to post page
    5. Check for errors (private account, comments disabled, etc.)
    6. Open comment box and post the first comment
    7. Verify comment was posted successfully
    8. Wait for network listener to capture request data
    """

    def __init__(self, ig, base_preparer):
        """
        Initialize the handler.

        Args:
            ig: Instagram browser automation instance (BasePlaywright)
            base_preparer: Parent BaseOrderPreparer instance for shared functionality
        """
        self.ig = ig
        self.base = base_preparer
        self.order = None
        self.first_action = None
        self.original_url = None
        self.normalized_link = None

    def prepare(self, order):
        """
        Main entry point for comment preparation.

        Executes the full preparation flow: validate, navigate, post comment, capture data.

        Args:
            order: Order model instance to prepare

        Raises:
            Exception: For permanent errors (invalid content, post deleted)
            LinkIsNotCorrect: For invalid URLs or disabled comments
            RetryableError: For temporary errors (failed to click button)
        """
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
        """
        Get the first OrderAction with comment content.

        For comment orders, OrderActions are created by Laravel with the
        comment text stored in the 'content' field. We need to find the
        first one with content to post via browser.

        Raises:
            Exception: If no action with content found or content is empty
        """
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
        """
        Validate that the target URL is a valid Instagram post/reel URL.

        Checks:
        - Domain is instagram.com
        - Path contains valid post/reel identifiers (/p/, /reel/, /reels/, /tv/)

        Raises:
            LinkIsNotCorrect: If URL format is invalid
        """
        parsed = urlparse(self.order.target_link)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            raise LinkIsNotCorrect("Invalid link, not an Instagram URL")

        path = parsed.path.strip('/').split('/')

        if len(path) < 2:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

        valid_first_segment = ["p", "reel", "reels", "tv"]

        # Check for formats like /p/ABC123 or /username/p/ABC123
        if len(path) == 2 and path[0] in valid_first_segment:
            return
        elif len(path) == 3 and path[1] in valid_first_segment:
            return
        else:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

    def _normalize_link(self):
        """
        Normalize the post URL for consistent behavior.

        Converts /reel/ and /reels/ URLs to /p/ format because:
        - Reel pages can auto-scroll to different content
        - /p/ URLs provide more stable comment interaction

        The original URL is preserved; we just use the normalized
        version for navigation.
        """
        url = self.order.target_link
        self.normalized_link = re.sub(r'/reels?/', '/p/', url)

        if self.normalized_link != url:
            self.ig.account.add_cli(f'Normalized link: {self.normalized_link}')

    def _setup_comment_listener(self):
        """
        Set up network listener to capture comment post request data.

        Listens for the PolarisPostCommentInputRevampedMutation GraphQL request
        and extracts media_id and doc_id from the request payload.

        These values are stored in self.base.captured_data for later use
        by the API execution phase.
        """

        def on_response(response):
            # Skip if we already captured data
            if self.base.captured_data:
                return

            try:
                # Only interested in GraphQL requests
                if '/graphql' not in response.url:
                    return

                # Check for comment mutation by header
                headers = response.request.headers
                friendly_name = headers.get('x-fb-friendly-name', '')

                if friendly_name != 'PolarisPostCommentInputRevampedMutation':
                    return

                post_data = response.request.post_data
                if not post_data:
                    return

                # Parse the POST data
                parsed = parse_qs(post_data, keep_blank_values=True)
                doc_id = parsed.get('doc_id', [''])[0]
                variables_str = parsed.get('variables', ['{}'])[0]

                try:
                    variables = json.loads(variables_str)
                except:
                    self.base._log_to_file(f'COMMENT_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                # Extract media_id from variables
                media_id = variables.get('media_id')

                if not media_id:
                    self.base._log_to_file(f'COMMENT_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

                # Store captured data for API execution phase
                self.base.captured_data = {
                    'media_id': str(media_id),
                    'doc_id': doc_id,
                }

                self.ig.account.add_cli(f'Comment data captured: {self.base.captured_data}')

            except Exception as e:
                self.base._log_to_file(f'COMMENT_LISTENER: {str(e)}', 'exception')

        # Register listener with base preparer for cleanup
        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _go_to_post_page(self):
        """
        Navigate browser to the post page using the normalized link.

        Uses normalized link (reel -> p) for more stable interaction.
        Waits longer than other handlers because comment UI takes time to load.
        """
        go_to_page(self.ig, self.normalized_link, 'Post Page')
        self.ig.pause(8000, 10000)

    def _check_post_errors(self):
        """
        Check for post page errors that prevent commenting.

        Detects various conditions:
        - Private account (can't comment)
        - Comments limited/disabled
        - Post deleted or unavailable
        - Page load errors
        - Comment box not visible (comments disabled)

        Also checks if we were redirected away from the post page,
        which can happen with private accounts.

        Raises:
            LinkIsNotCorrect: For permanent issues with the post
            RetryableError: For temporary load errors
        """
        self.original_url = self.ig.page.url

        # Check if redirected away from post (e.g., private account redirects to profile)
        if '/p/' not in self.original_url and '/reel/' not in self.original_url and '/reels/' not in self.original_url:
            raise LinkIsNotCorrect("Account is private or post isn't available")

        # Check for private account message
        if self.ig.is_visible_by_text('This account is private'):
            raise LinkIsNotCorrect('Account is private')

        # Check for limited comments
        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            raise LinkIsNotCorrect('Comments on this post have been limited')

        # Check for deleted/unavailable post
        if self.ig.is_visible_by_text("Post isn't available") or \
           self.ig.is_visible_by_text("The link may be broken") or \
           self.ig.is_visible_by_text("the profile may have been removed"):
            raise LinkIsNotCorrect("Post isn't available")

        # Check for page not found errors
        if self.ig.is_visible_by_text("Sorry, this page isn't available") or \
           self.ig.is_visible_by_text("Page is not available") or \
           self.ig.is_visible_by_text("This page isn't available"):
            raise LinkIsNotCorrect("Page is not available")

        # Check for temporary load errors
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise RetryableError("Page load issue - temporary error")

        # Verify comment functionality is available
        # If like button visible but comment button not, comments are likely disabled
        comment_locator = self.ig.page.locator('svg[aria-label="Comment"]').first
        like_locator = self.ig.page.locator('svg[aria-label="Like"]').first

        if like_locator.is_visible() and not comment_locator.is_visible():
            raise LinkIsNotCorrect("Comment box is not visible")

    def _dismiss_popup(self):
        """
        Dismiss any Instagram popups that might block interaction.

        Common popups include "shared this with you" and "Stay up to date with"
        notifications that can overlay the comment input.
        """
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(1000, 1500)
            except:
                pass

    def _open_comment_box(self):
        """
        Open the comment input box for reels.

        Reels have a different UI where you need to click the comment icon
        to open the comment input. Regular posts show the input directly.

        Also verifies we're still on the same post after clicking, since
        reels can auto-scroll to different content.
        """
        # Only needed for reels
        if 'reels' in self.ig.page.url or 'reel' in self.ig.page.url:
            try:
                # Try clicking comment icon
                self.ig.page.locator("svg[aria-label='Comment']").first.click(timeout=5000)
                self.ig.pause(5000, 6500)
            except:
                try:
                    # Fallback: click button containing comment icon
                    self.ig.page.locator("div[role='button']").filter(
                        has=self.ig.page.locator("svg[aria-label='Comment']")
                    ).click(timeout=5000)
                    self.ig.pause(5000, 6500)
                except Exception as e:
                    self.ig.account.add_cli(f'Open comment box error: {str(e)}')

            # Verify we didn't scroll to a different post
            self._verify_still_on_same_post()

    def _verify_still_on_same_post(self):
        """
        Verify the browser is still on the same post.

        Reels can auto-scroll to different content, which would cause us
        to post a comment on the wrong post. This check ensures we're
        still on the intended post.

        Raises:
            RetryableError: If we've navigated to a different post
        """
        current_url = self.ig.page.url

        # Extract media shortcodes to compare
        original_id = self._extract_media_id_from_url(self.original_url)
        current_id = self._extract_media_id_from_url(current_url)

        if original_id and current_id and original_id != current_id:
            raise RetryableError(f"Navigated to different post: {current_id} instead of {original_id}")

        # Also check we're still on a post page at all
        if '/reel/' not in current_url and '/p/' not in current_url and '/reels/' not in current_url:
            raise RetryableError("Left post page unexpectedly")

    def _extract_media_id_from_url(self, url):
        """
        Extract the media shortcode from an Instagram URL.

        The shortcode is the unique identifier in URLs like:
        - instagram.com/p/ABC123/
        - instagram.com/reel/ABC123/

        Args:
            url: Full Instagram URL

        Returns:
            Shortcode string or None if not found
        """
        match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    def _post_comment(self):
        """
        Post the first comment via browser automation.

        Finds the comment input, types the comment text, and clicks Post.
        This triggers the GraphQL request that our listener captures.

        Raises:
            LinkIsNotCorrect: If comments are disabled
            RetryableError: If post button not found or other temporary issues
        """
        comment_text = self.first_action.content

        try:
            # Find comment input field
            comment_input = self.ig.page.get_by_placeholder("Add a comment…")

            if comment_input.count() == 0:
                raise LinkIsNotCorrect("Comments are disabled on this post")

            if not comment_input.is_visible():
                raise LinkIsNotCorrect("Comment input is not visible - comments may be disabled")

            # Type the comment text
            comment_input.fill(comment_text, timeout=5000)
            self.ig.pause(2500, 4000)

            # Find and click Post button
            post_button = self.ig.page.get_by_role("button", name="Post", exact=True)

            if post_button.count() == 0 or not post_button.is_visible():
                raise RetryableError("Post button not found")

            post_button.click()
            self.ig.pause(3000, 4000)

            # Verify we're still on the same post after posting
            self._verify_still_on_same_post()

        except LinkIsNotCorrect:
            raise
        except RetryableError:
            raise
        except Exception as e:
            raise RetryableError(f"Failed to post comment: {str(e)}")

    def _verify_comment_posted(self):
        """
        Verify the comment was posted successfully.

        Checks for error messages that indicate the comment failed.
        Note: Success is primarily verified by the network listener
        capturing the GraphQL request.

        Raises:
            Exception: If comment posting error message is visible
        """
        self.ig.pause(3000, 4500)

        if self.ig.is_visible_by_text("Couldn't post comment"):
            raise Exception("Couldn't post comment")

        self.ig.account.add_cli("Comment posted successfully")