import json
from urllib.parse import parse_qs, urlparse

from script.extra.helper import go_to_page
from ..LinkParser import LinkParser
from script.extra.exceptions import RetryableError


class SavePostPrepareHandler:
    """
    Handler for preparing save_post orders.

    This handler navigates to an Instagram post via browser, clicks the save button,
    and captures the GraphQL request data needed for subsequent API-based saves.

    The captured data (media_id, doc_id) is stored in order.action_data and used
    by BrowserApiSavePostEvent to perform remaining saves via direct API calls.

    Flow:
    1. Parse and validate the post/reel URL
    2. Set up network listener to capture save request
    3. Navigate to post page
    4. Check for errors (private account, deleted post, etc.)
    5. Click save button (unsave first if already saved)
    6. Verify save was successful
    7. Wait for network listener to capture the request data
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
        self.parsed_link = None
        self.is_reel = False

    def prepare(self, order):
        """
        Main entry point for save_post preparation.

        Executes the full preparation flow: navigate, save, capture data.

        Args:
            order: Order model instance to prepare

        Raises:
            Exception: For permanent errors (private account, deleted post)
            RetryableError: For temporary errors (failed to click button)
        """
        self.order = order

        self._parse_link()
        self._setup_save_listener()
        self._go_to_post_page()
        self._check_post_errors()
        self._dismiss_popup()
        self._click_save_button()
        self._verify_saved()
        self.base.wait_for_capture()

    def _parse_link(self):
        """
        Parse and validate the target link.

        Ensures the URL is a valid Instagram post or reel URL.
        Also determines if the content is a reel (affects UI interactions).

        Raises:
            Exception: If link is not a valid post/reel URL
        """
        self.parsed_link = LinkParser.parse(self.order.target_link)

        if not LinkParser.is_post_or_reel(self.order.target_link):
            raise Exception('Link is not a valid post or reel URL')

        self.is_reel = LinkParser.is_reel(self.order.target_link)

    def _validate_post_url(self):
        """
        Validate that the URL is a properly formatted Instagram post/reel URL.

        Checks:
        - Domain is instagram.com
        - Path contains valid post/reel identifiers (/p/, /reel/, /tv/)

        Raises:
            Exception: If URL format is invalid
        """
        parsed = urlparse(self.order.target_link)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            raise Exception("Invalid link, not an Instagram URL")

        path = parsed.path.strip('/').split('/')

        if len(path) == 1:
            raise Exception("Not a valid Instagram post or reel")

        valid_first_segment = ["p", "reel", "tv"]

        # Check for formats like /p/ABC123 or /username/p/ABC123
        if len(path) == 2 and path[0] in valid_first_segment:
            return True
        elif len(path) == 3 and path[1] in valid_first_segment:
            return True
        else:
            raise Exception("Not a valid Instagram post or reel")

    def _setup_save_listener(self):
        """
        Set up network listener to capture save post GraphQL request.

        Listens for the usePolarisSaveMediaSaveMutation GraphQL request
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

                post_data = response.request.post_data
                if not post_data:
                    return

                # Parse the POST data
                parsed = parse_qs(post_data, keep_blank_values=True)
                fb_api_name = parsed.get('fb_api_req_friendly_name', [''])[0]

                # Only interested in save mutation requests
                if fb_api_name != 'usePolarisSaveMediaSaveMutation':
                    return

                # Extract variables and doc_id from request
                variables_str = parsed.get('variables', ['{}'])[0]
                doc_id = parsed.get('doc_id', [''])[0]

                try:
                    variables = json.loads(variables_str)
                except:
                    self.base._log_to_file(f'SAVE_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                # Validate required field is present
                if 'media_id' not in variables:
                    self.base._log_to_file(f'SAVE_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

                # Store captured data for API execution phase
                self.base.captured_data = {
                    'media_id': str(variables.get('media_id', '')),
                    'doc_id': doc_id,
                }

                self.ig.account.add_cli(f'Save post data captured: {self.base.captured_data}')

            except Exception as e:
                self.base._log_to_file(f'SAVE_LISTENER: {str(e)}', 'exception')

        # Register listener with base preparer for cleanup
        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _go_to_post_page(self):
        """
        Navigate browser to the post page.

        Uses the original target_link from the order.
        Waits for page to fully load before continuing.
        """
        go_to_page(self.ig, self.order.target_link, 'Post Page')
        self.ig.pause(6000, 8000)

    def _check_post_errors(self):
        """
        Check for common post page errors.

        Detects various error conditions and categorizes them:

        Account-level issues (our automation account has a problem):
        - Redirect to login/challenge/consent → RetryableError (another account should try)

        Post-level issues (the target post/account is inaccessible):
        - Redirect to profile page → Exception (cancel + charge)
        - Private account message → Exception
        - Deleted/unavailable post → Exception

        Temporary issues:
        - Page load errors → RetryableError

        Raises:
            Exception: For permanent issues with the post (cancel + charge)
            RetryableError: For temporary issues (retry with another account)
        """
        current_url = self.ig.page.url

        # Check if redirected away from post page
        if '/p/' not in current_url and '/reel/' not in current_url and '/reels/' not in current_url:
            self.ig.account.add_cli(f'Redirected to: {current_url}')

            # Check if redirect is due to our account's issue (login/challenge/consent)
            # These are temporary — another account should try this order
            account_issue_paths = ['/accounts/login', '/challenge', '/consent']
            is_account_issue = any(path in current_url for path in account_issue_paths)

            # Redirect to Instagram home page is also likely an account issue
            if is_account_issue or current_url.rstrip('/') in ['https://www.instagram.com', 'https://instagram.com']:
                raise RetryableError(
                    f"Account issue detected (redirected to {current_url})"
                )

            # Any other redirect (e.g., to profile page) means the post is inaccessible
            raise Exception("Account is private or post isn't available (redirected away from post)")

        # Check for private account messages
        # Instagram uses different text variants depending on the UI version
        if self.ig.is_visible_by_text('This account is private') or \
           self.ig.is_visible_by_text('This profile is private'):
            raise Exception('Account is private')

        # Check for deleted/unavailable post
        if self.ig.is_visible_by_text("Post isn't available") or \
           self.ig.is_visible_by_text("The link may be broken") or \
           self.ig.is_visible_by_text("the profile may have been removed"):
            raise Exception("Post isn't available")

        # Check for page not found errors
        if self.ig.is_visible_by_text("Sorry, this page isn't available") or \
           self.ig.is_visible_by_text("Page is not available") or \
           self.ig.is_visible_by_text("This page isn't available"):
            raise Exception("Page is not available")

        # Check for temporary load errors
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise RetryableError("Page load issue - temporary error")

    def _dismiss_popup(self):
        """
        Dismiss any Instagram popups that might block interaction.

        Common popups include "shared this with you" and "Stay up to date with"
        notifications. These need to be dismissed before we can interact with
        the save button.
        """
        self.ig.pause(1000, 1200)

        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(1000, 1500)
            except Exception as e:
                self.ig.account.add_cli(f'Dismiss popup error: {str(e)}')

    def _click_save_button(self):
        """
        Click the save button to save the post.

        If the post is already saved, it first unsaves it, then saves again.
        This ensures we always capture the save request data.

        Raises:
            RetryableError: If save button cannot be clicked
        """
        self.ig.account.add_cli("Attempting to save post...")

        # If already saved, unsave first so we can capture the save request
        if self._is_saved():
            self.ig.account.add_cli("Post is already saved, unsaving first...")
            self._unsave_post()
            self.ig.pause(4000, 6000)

        # Click save button
        if not self._try_save():
            raise RetryableError("Failed to click save button")

        self.ig.pause(3000, 5000)

    def _try_save(self):
        """
        Attempt to click the save button using various selectors.

        Instagram's UI can vary, so we try multiple CSS selectors
        to find and click the save button.

        Returns:
            True if save button was clicked successfully
            False if no save button could be found/clicked
        """
        # Multiple selectors for different Instagram UI versions
        selectors = [
            'div[role="button"]:has(svg[aria-label="Save"])',
            'div.x14z9mp.xvc5jky div[role="button"]:has(svg[aria-label="Save"])',
            'section div[role="button"]:has(svg) >> nth=2',
            'div[data-visualcompletion="ignore-dynamic"] div[role="button"]:has(svg[aria-label="Save"])',
            'svg[aria-label="Save"]',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    return True
            except:
                continue

        return False

    def _unsave_post(self):
        """
        Unsave the post by clicking the remove/unsave button.

        Called when post is already saved and we need to unsave it
        first before saving again to capture the request data.

        Returns:
            True if unsave button was clicked successfully
            False if no unsave button could be found/clicked
        """
        # Selectors for unsave/remove button
        selectors = [
            'svg[aria-label="Remove"]',
            'svg[aria-label="Unsave"]',
            'div[role="button"]:has(svg[aria-label="Remove"])',
            'div[role="button"]:has(svg[aria-label="Unsave"])',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    return True
            except:
                continue

        return False

    def _is_saved(self):
        """
        Check if the post is already saved.

        Looks for the "Remove" or "Unsave" button/icon which indicates
        the post is currently saved.

        Returns:
            True if post appears to be saved
            False otherwise
        """
        # Selectors that indicate post is saved
        selectors = [
            'svg[aria-label="Remove"]',
            'svg[aria-label="Unsave"]',
            'div[role="button"]:has(svg[aria-label="Remove"])',
            'div[role="button"]:has(svg[aria-label="Unsave"])',
        ]

        for selector in selectors:
            try:
                if self.ig.page.locator(selector).first.count() > 0:
                    if self.ig.page.locator(selector).first.is_visible():
                        return True
            except:
                continue

        return False

    def _verify_saved(self):
        """
        Verify that the post was saved successfully.

        After clicking save, we verify the save state changed by checking
        for the unsave button. This confirms the action completed.

        Raises:
            RetryableError: If verification fails (save didn't work)
        """
        self.ig.pause(2000, 4000)

        if not self._is_saved():
            raise RetryableError("Post was not saved - verification failed")

        self.ig.account.add_cli("Post saved successfully")