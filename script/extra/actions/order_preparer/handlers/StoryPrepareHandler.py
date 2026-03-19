import json
import re
import time
from urllib.parse import parse_qs

from script.extra.helper import go_to_page
from ..LinkParser import LinkParser
from script.extra.exceptions import RetryableError


# Maximum time to wait for profile data to be captured
CAPTURE_TIMEOUT_SECONDS = 45


class StoryPrepareHandler:
    """
    Handler for preparing view_story orders.

    This handler navigates to an Instagram story via browser, views it,
    and captures the GraphQL request data needed for subsequent API-based views.

    Supports two types of links:
    1. Direct story link: instagram.com/stories/username/story_id
    2. Username/profile link: instagram.com/username (navigates to their story)

    The captured data (reelId, reelMediaId, etc.) is stored in order.action_data
    and used by BrowserApiViewStoryEvent to perform remaining views via direct API calls.

    Flow for direct story link:
    1. Set up network listener
    2. Navigate directly to story
    3. Click "View story" button if present
    4. Wait for data capture

    Flow for username link:
    1. Navigate to profile to check if story exists and account is public
    2. Navigate to story URL
    3. View story and capture data
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
        self.target_username = None
        self.profile_data = None

    def prepare(self, order):
        """
        Main entry point for story preparation.

        Routes to appropriate flow based on link type:
        - Direct story links go straight to story page
        - Username links first check profile, then navigate to story

        Args:
            order: Order model instance to prepare

        Raises:
            Exception: For permanent errors (private account, no story, expired)
            RetryableError: For temporary errors
            TimeoutError: If data capture times out
        """
        self.order = order

        self._parse_link()

        if self.parsed_link['type'] == LinkParser.TYPE_STORY:
            # Direct story link - go straight to story
            self._process_direct_story_link()
        else:
            # Username link - check profile first, then go to story
            self._process_username_link()

    def _parse_link(self):
        """
        Parse and validate the target link to determine link type and extract username.

        Determines:
        - Link type (story, profile, post/reel)
        - Target username (from URL or extracted from post page)

        Raises:
            Exception: If highlights (not supported) or if username cannot be determined
        """
        self.parsed_link = LinkParser.parse(self.order.target_link)

        # Highlights are not supported for view_story orders
        if self.parsed_link['type'] == LinkParser.TYPE_HIGHLIGHT:
            raise Exception('Highlights are not supported')

        # Direct story link - username is in the URL
        if self.parsed_link['type'] == LinkParser.TYPE_STORY:
            self.target_username = self.parsed_link['username']
            return

        # Profile link - username is in the URL
        if self.parsed_link['username']:
            self.target_username = self.parsed_link['username']
            return

        # Post/reel link - need to extract username from the page
        if LinkParser.needs_username_extraction(self.order.target_link):
            self.target_username = self._extract_username_from_post()
            return

        raise Exception('Could not determine username from link')

    def _process_direct_story_link(self):
        """
        Process a direct story link (instagram.com/stories/username/story_id).

        For direct links, we can go straight to the story page without
        first checking the profile. This is faster but may fail if the
        story has expired.
        """
        self._setup_story_listener()

        # Navigate directly to story URL
        go_to_page(self.ig, self.order.target_link, 'Story Page')
        self.ig.pause(5000, 7000)

        self._check_story_errors()
        self._click_view_story()
        self.base.wait_for_capture()

    def _process_username_link(self):
        """
        Process a username/profile link.

        For username links, we first navigate to the profile to:
        1. Check if account is public (private accounts can't be viewed)
        2. Check if user has an active story (latest_reel_media > 0)

        Then we navigate to the story URL and capture the view data.
        """
        # First, check profile for story availability
        self._setup_profile_listener()

        profile_url = f'https://www.instagram.com/{self.target_username}/'
        go_to_page(self.ig, profile_url, 'Profile Page')
        self.ig.pause(6000, 8000)

        self._check_page_errors()
        self._wait_for_profile_data()
        self._validate_profile_data()

        # Profile is good - now navigate to story
        self._remove_profile_listener()
        self._setup_story_listener()

        story_url = f'https://www.instagram.com/stories/{self.target_username}/'
        go_to_page(self.ig, story_url, 'Story Page')
        self.ig.pause(6000, 8000)

        self._check_story_errors()
        self._click_view_story()
        self.base.wait_for_capture()

    def _setup_profile_listener(self):
        """
        Set up network listener to capture profile data.

        Listens for the PolarisProfilePageContentQuery GraphQL response
        to extract profile information including:
        - is_private: Whether account is private
        - latest_reel_media: Timestamp of latest story (0 if no story)
        - pk: User ID
        - username: Username

        This data is used to validate the order can be completed before
        attempting to view the story.
        """
        self.profile_data = None

        def on_response(response):
            # Skip if we already have profile data
            if self.profile_data:
                return

            try:
                # Only interested in GraphQL requests
                if '/graphql' not in response.url:
                    return

                # Check for profile query by header
                headers = response.request.headers
                friendly_name = headers.get('x-fb-friendly-name', '')

                if friendly_name != 'PolarisProfilePageContentQuery':
                    return

                # Parse response JSON
                try:
                    json_data = response.json()
                except:
                    return

                # Extract user data from response
                user_data = json_data.get('data', {}).get('user', {})

                if not user_data:
                    self.base._log_to_file(f'PROFILE_NO_USER: {json.dumps(json_data)[:500]}', 'unknown')
                    return

                # Store relevant profile data
                self.profile_data = {
                    'is_private': user_data.get('is_private', False),
                    'latest_reel_media': user_data.get('latest_reel_media', 0),
                    'pk': user_data.get('pk', ''),
                    'username': user_data.get('username', ''),
                }

            except Exception as e:
                self.base._log_to_file(f'PROFILE_LISTENER: {str(e)}', 'exception')

        # Register listener with base preparer for cleanup
        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _remove_profile_listener(self):
        """
        Remove the profile listener.

        Note: Actual removal is handled by base._cleanup_listeners() at the end.
        This is a placeholder for explicit removal if needed in the future.
        """
        pass  # Will be cleaned up by base._cleanup_listeners()

    def _wait_for_profile_data(self):
        """
        Wait for profile data to be captured by the network listener.

        Polls for profile_data to be populated with a timeout.

        Raises:
            TimeoutError: If profile data not captured within timeout
        """
        start = time.time()

        while time.time() - start < CAPTURE_TIMEOUT_SECONDS:
            if self.profile_data:
                return
            time.sleep(0.3)

        raise TimeoutError('Timeout waiting for profile data')

    def _validate_profile_data(self):
        """
        Validate captured profile data to ensure story is viewable.

        Checks:
        - Profile data was captured
        - Account is not private
        - User has an active story (latest_reel_media > 0)

        Raises:
            RetryableError: If no profile data was captured
            Exception: If account is private or has no story
        """
        if not self.profile_data:
            raise RetryableError('No profile data captured')

        if self.profile_data.get('is_private'):
            raise Exception('Account is private')

        # latest_reel_media is timestamp of latest story, 0 means no story
        latest_reel = self.profile_data.get('latest_reel_media', 0)
        if not latest_reel or latest_reel == 0:
            raise Exception('User has no active story')

    def _setup_story_listener(self):
        """
        Set up network listener to capture story view request data.

        Listens for the StoriesV3SeenMutation GraphQL request which is sent
        when a story is viewed. Extracts the required fields:
        - doc_id: GraphQL document ID
        - reelId: Reel/story container ID
        - reelMediaId: Individual story media ID
        - reelMediaOwnerId: Story owner's user ID
        - reelMediaTakenAt: Timestamp when story was posted

        This data is stored in self.base.captured_data for use by the
        API execution phase.
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

                # Only interested in story seen mutation
                if 'StoriesV3SeenMutation' not in fb_api_name:
                    return

                # Extract variables and doc_id from request
                variables_str = parsed.get('variables', ['{}'])[0]
                doc_id = parsed.get('doc_id', [''])[0]

                try:
                    variables = json.loads(variables_str)
                except:
                    self.base._log_to_file(f'STORY_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                # Validate required field is present
                if 'reelMediaId' not in variables:
                    self.base._log_to_file(f'STORY_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

                # Store captured data for API execution phase
                self.base.captured_data = {
                    'doc_id': doc_id,
                    'reelId': str(variables.get('reelId', '')),
                    'reelMediaId': str(variables.get('reelMediaId', '')),
                    'reelMediaOwnerId': str(variables.get('reelMediaOwnerId', '')),
                    'reelMediaTakenAt': variables.get('reelMediaTakenAt', 0),
                }

                self.ig.account.add_cli(f'Story data captured: {self.base.captured_data}')

            except Exception as e:
                self.base._log_to_file(f'STORY_LISTENER: {str(e)}', 'exception')

        # Register listener with base preparer for cleanup
        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _click_view_story(self):
        """
        Click the "View story" button if present.

        Some story pages show a "View story" button that must be clicked
        before the story viewer opens. This is common for stories with
        age restrictions or sensitive content.

        If no button is present, the story viewer opens automatically.
        """
        try:
            # Check if "View story" button exists
            if not self.ig.is_visible_by_text('View story'):
                return

            # Try various selectors for the button
            selectors = [
                'div[role="button"]:has-text("View story")',
                'button:has-text("View story")',
            ]

            for selector in selectors:
                try:
                    btn = self.ig.page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click(timeout=5000)
                        self.ig.pause(3000, 4000)
                        return
                except:
                    continue

            # Fallback: use role-based selector
            self.ig.page.get_by_role('button', name=re.compile(r'View story', re.I)).click(timeout=5000)
            self.ig.pause(3000, 4000)

        except Exception as e:
            self.ig.account.add_cli(f'Click view story error: {str(e)}')

    def _check_page_errors(self):
        """
        Check for common page errors on profile page.

        These errors indicate the profile doesn't exist, has been removed,
        or is private (which prevents story viewing).

        Also detects account-level redirects (login/challenge/consent) which
        indicate our automation account has an issue, not the target profile.

        Raises:
            Exception: For permanent issues with the profile
            RetryableError: For temporary account issues
        """
        current_url = self.ig.page.url

        # Check if redirected to login/challenge/consent (our account's issue)
        account_issue_paths = ['/accounts/login', '/challenge', '/consent']
        is_account_issue = any(path in current_url for path in account_issue_paths)

        if is_account_issue or current_url.rstrip('/') in ['https://www.instagram.com', 'https://instagram.com']:
            self.ig.account.add_cli(f'Redirected to: {current_url}')
            raise RetryableError(
                f"Account issue detected (redirected to {current_url})"
            )

        # Check for private account messages
        # Instagram uses different text variants depending on the UI version
        if self.ig.is_visible_by_text('This account is private') or \
           self.ig.is_visible_by_text('This profile is private'):
            raise Exception('Account is private')

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
        """
        Check for story-specific errors.

        Detects various conditions and categorizes them:

        Account-level issues (our automation account has a problem):
        - Redirect to login/challenge/consent → RetryableError (another account should try)

        Story-level issues (the target story/account is inaccessible):
        - Story unavailable flag in URL → Exception (cancel + charge)
        - Redirect to non-story page (profile, home) → Exception
        - Private account message → Exception

        Temporary issues:
        - Page load errors → RetryableError

        Raises:
            Exception: For permanent issues with the story (cancel + charge)
            RetryableError: For temporary issues (retry with another account)
        """
        current_url = self.ig.page.url

        # Check URL for unavailable flag
        if 'show_story_unavailable=1' in current_url:
            raise Exception('Story is unavailable')

        # Check if redirected away from stories page
        if '/stories/' not in current_url:
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

            # Any other redirect means the story/user is not accessible
            raise Exception('User has no active story')

        # Check for visible error messages
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

        # Check for temporary page load errors
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise RetryableError("Page load issue - temporary error")

        # Check for private account messages
        # Instagram uses different text variants depending on the UI version
        if self.ig.is_visible_by_text('This account is private') or \
           self.ig.is_visible_by_text('This profile is private'):
            raise Exception('Account is private')

    def _extract_username_from_post(self):
        """
        Extract username from a post/reel page.

        When the order target is a post/reel URL, we need to navigate to it
        and find the username of the post author to then view their story.

        Looks for the username link in the post header.

        Returns:
            Username string

        Raises:
            RetryableError: If username cannot be extracted
        """
        # Navigate to post page
        go_to_page(self.ig, self.order.target_link, 'Post Page')
        self.ig.pause(4000, 5000)

        self._check_page_errors()

        # Selectors for username link in post header
        selectors = [
            'header a[href^="/"][role="link"]',
            'article header a[href^="/"]',
            'a._a6hd[href^="/"][role="link"]',
        ]

        # Try each selector to find username
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

        raise RetryableError('Could not extract username from post')

    def _parse_username_from_href(self, href):
        """
        Parse username from an href attribute.

        Validates the extracted string is a valid Instagram username:
        - Not a reserved path (p, reel, explore, etc.)
        - Reasonable length (<=30 chars)
        - Valid characters only (letters, numbers, underscores, periods)

        Args:
            href: The href attribute value to parse

        Returns:
            Username string or None if invalid
        """
        if not href or href == '#':
            return None

        # Extract first path segment
        href = href.strip('/').split('/')[0]

        # Remove query parameters
        if '?' in href:
            href = href.split('?')[0]

        # Skip reserved Instagram paths
        reserved = ['p', 'reel', 'reels', 'stories', 'explore', 'direct', 'accounts', 'tv', 'tags', 'locations']
        if href.lower() in reserved:
            return None

        # Validate username format
        if not href or len(href) > 30:
            return None

        if not re.match(r'^[a-zA-Z0-9_.]+$', href):
            return None

        return href