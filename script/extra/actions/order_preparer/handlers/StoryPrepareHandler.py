import json
import re
import time
from urllib.parse import parse_qs

from script.extra.helper import go_to_page
from ..LinkParser import LinkParser
from ..BaseOrderPreparer import RetryableError


CAPTURE_TIMEOUT_SECONDS = 30


class StoryPrepareHandler:
    """Handler for preparing view_story orders"""

    def __init__(self, ig, base_preparer):
        self.ig = ig
        self.base = base_preparer
        self.order = None
        self.parsed_link = None
        self.target_username = None
        self.profile_data = None

    def prepare(self, order):
        """Main entry point for story preparation"""
        self.order = order

        self._parse_link()

        if self.parsed_link['type'] == LinkParser.TYPE_STORY:
            self._process_direct_story_link()
        else:
            self._process_username_link()

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
        self.base.wait_for_capture()

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
        self.base.wait_for_capture()

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
                    self.base._log_to_file(f'PROFILE_NO_USER: {json.dumps(json_data)[:500]}', 'unknown')
                    return

                self.profile_data = {
                    'is_private': user_data.get('is_private', False),
                    'latest_reel_media': user_data.get('latest_reel_media', 0),
                    'pk': user_data.get('pk', ''),
                    'username': user_data.get('username', ''),
                }

            except Exception as e:
                self.base._log_to_file(f'PROFILE_LISTENER: {str(e)}', 'exception')

        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _remove_profile_listener(self):
        """Remove profile listener"""
        pass  # Will be cleaned up by base._cleanup_listeners()

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
            raise RetryableError('No profile data captured')

        if self.profile_data.get('is_private'):
            raise Exception('Account is private')

        latest_reel = self.profile_data.get('latest_reel_media', 0)
        if not latest_reel or latest_reel == 0:
            raise Exception('User has no active story')

    def _setup_story_listener(self):
        """Listen for story seen request"""

        def on_response(response):
            if self.base.captured_data:
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
                    self.base._log_to_file(f'STORY_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                if 'reelMediaId' not in variables:
                    self.base._log_to_file(f'STORY_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

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

        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

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

        raise RetryableError('Could not extract username from post')

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