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
        Waits longer than other handlers because comment UI takes extra time
        to fully render, especially for reel content loaded via /p/ URL.
        """
        go_to_page(self.ig, self.normalized_link, 'Post Page')
        self.ig.pause(10000, 13000)

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
        # When accessing a private account's post, Instagram silently redirects to the
        # profile page instead of showing the post. We detect this by checking if the
        # current URL still contains a post/reel path segment.
        if '/p/' not in self.original_url and '/reel/' not in self.original_url and '/reels/' not in self.original_url:
            self.ig.account.add_cli(f'Redirected to: {self.original_url}')
            raise LinkIsNotCorrect("Account is private or post isn't available (redirected away from post)")

        # Check for private account messages
        # Instagram uses different text variants depending on the UI version
        if self.ig.is_visible_by_text('This account is private') or \
           self.ig.is_visible_by_text('This profile is private'):
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
        Waits before checking to allow popup animation to complete.
        """
        self.ig.pause(1500, 2500)

        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(2000, 3000)
            except Exception:
                pass

    def _open_comment_box(self):
        """
        Ensure the comment input is visible and ready for interaction.

        Uses UI-based detection instead of URL-based detection because:
        - Normalized reel URLs (/p/) may still render with reel-like UI
        - Instagram can show different layouts regardless of the URL format
        - The comment input might be hidden behind the Comment icon click

        Logic:
        1. Check if comment input (placeholder) is already visible
        2. If visible -> done, no action needed (typical for regular posts)
        3. If not visible -> look for Comment icon (svg[aria-label="Comment"])
        4. If icon found -> click it to reveal the comment input
        5. If icon not found -> comments are likely disabled (handled by _post_comment)

        After clicking the icon, verifies we're still on the same post
        since reels can auto-scroll to different content.
        """
        # Check if comment input is already visible (common for regular /p/ posts)
        comment_input = self.ig.page.get_by_placeholder("Add a comment…")

        try:
            if comment_input.count() > 0 and comment_input.is_visible():
                self.ig.account.add_cli('Comment input already visible, no need to click icon')
                return
        except Exception:
            pass

        self.ig.account.add_cli('Comment input not visible, looking for Comment icon...')

        # Comment input is not visible - try clicking the Comment icon to reveal it
        # This is needed for reels and some post layouts where the input is hidden
        comment_icon_clicked = False

        # Selector 1: Direct SVG icon click
        try:
            icon = self.ig.page.locator("svg[aria-label='Comment']").first
            if icon.count() > 0 and icon.is_visible():
                icon.click(timeout=5000)
                comment_icon_clicked = True
                self.ig.account.add_cli('Clicked Comment icon (svg)')
                self.ig.pause(5000, 7000)
        except Exception:
            pass

        # Selector 2: Parent button wrapping the Comment icon (fallback)
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

        # Selector 3: The span > div[role=button] wrapper seen in some UI versions
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
            # No comment icon found - this will be handled by _post_comment
            # which checks for the input and raises appropriate error
            self.ig.account.add_cli('Comment icon not found, will check input in next step')
            return

        # After clicking the icon, verify we didn't scroll to a different post
        # This can happen on reel pages where clicking triggers auto-scroll
        self._verify_still_on_same_post()

        # Extra wait after icon click for the comment input to fully render
        self.ig.pause(2000, 3000)

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

        Detection order:
        1. Check for restricted/disabled placeholders (e.g., "Comments on this post have been limited")
           If found -> permanent error, no point retrying
        2. Check for normal comment input ("Add a comment…")
           If found -> proceed to type and post
        3. If normal input not found -> check Comment icon to distinguish timing vs disabled

        Raises:
            LinkIsNotCorrect: If comments are permanently disabled on this post
            RetryableError: If post button not found or comment input not loaded yet
        """
        comment_text = self.first_action.content

        try:
            # Step 1: Check for restricted/disabled placeholders BEFORE looking for the normal input
            # Instagram replaces the normal "Add a comment…" placeholder with these messages
            # when commenting is restricted. The input element still exists but is non-functional.
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

            # Step 2: Find the normal comment input field by placeholder text
            comment_input = self.ig.page.get_by_placeholder("Add a comment…")

            # Check if the comment input is available and visible
            input_found = comment_input.count() > 0 and comment_input.is_visible()

            if not input_found:
                # Step 3: Input not visible - determine if comments are disabled or just not loaded
                # Check if the Comment icon (svg) exists on the page
                comment_icon = self.ig.page.locator('svg[aria-label="Comment"]').first
                icon_exists = False

                try:
                    icon_exists = comment_icon.count() > 0 and comment_icon.is_visible()
                except Exception:
                    pass

                if icon_exists:
                    # Comment icon exists but input is not visible
                    # This means comments ARE enabled, but the input hasn't rendered yet
                    # (could be a timing issue, or the icon click in _open_comment_box didn't work)
                    raise RetryableError(
                        "Comment icon is visible but input is not loaded - possible timing issue"
                    )
                else:
                    # No comment icon and no comment input - comments are truly disabled
                    raise LinkIsNotCorrect("Comments are disabled on this post")

            # Comment input is visible - type the comment text
            self.ig.account.add_cli(f'Typing comment: {comment_text[:40]}...')
            comment_input.fill(comment_text, timeout=5000)
            self.ig.pause(3000, 5000)

            # Find and click Post button
            # Wait a moment for Instagram to enable the button after text input
            post_button = self.ig.page.get_by_role("button", name="Post", exact=True)

            if post_button.count() == 0 or not post_button.is_visible():
                # Post button not found after typing - could be a timing issue
                # or Instagram hasn't enabled it yet. Give it one more chance.
                self.ig.account.add_cli('Post button not visible yet, waiting...')
                self.ig.pause(3000, 4000)

                if post_button.count() == 0 or not post_button.is_visible():
                    raise RetryableError("Post button not found after extended wait")

            post_button.click()
            self.ig.pause(4000, 6000)

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

        Waits before checking to allow Instagram to display any error messages.

        Raises:
            Exception: If comment posting error message is visible
        """
        self.ig.pause(4000, 6000)

        if self.ig.is_visible_by_text("Couldn't post comment"):
            raise Exception("Couldn't post comment")

        self.ig.account.add_cli("Comment posted successfully")