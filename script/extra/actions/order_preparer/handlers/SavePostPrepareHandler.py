import json
from urllib.parse import parse_qs, urlparse

from script.extra.helper import go_to_page
from ..LinkParser import LinkParser


class SavePostPrepareHandler:
    """Handler for preparing save_post orders"""

    def __init__(self, ig, base_preparer):
        self.ig = ig
        self.base = base_preparer
        self.order = None
        self.parsed_link = None
        self.is_reel = False

    def prepare(self, order):
        """Main entry point for save_post preparation"""
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
        """Parse and validate link"""
        self.parsed_link = LinkParser.parse(self.order.target_link)

        if not LinkParser.is_post_or_reel(self.order.target_link):
            raise Exception('Link is not a valid post or reel URL')

        self.is_reel = LinkParser.is_reel(self.order.target_link)

    def _validate_post_url(self):
        """Validate that URL is a valid Instagram post/reel"""
        parsed = urlparse(self.order.target_link)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            raise Exception("Invalid link, not an Instagram URL")

        path = parsed.path.strip('/').split('/')

        if len(path) == 1:
            raise Exception("Not a valid Instagram post or reel")

        valid_first_segment = ["p", "reel", "tv"]

        if len(path) == 2 and path[0] in valid_first_segment:
            return True
        elif len(path) == 3 and path[1] in valid_first_segment:
            return True
        else:
            raise Exception("Not a valid Instagram post or reel")

    def _setup_save_listener(self):
        """Listen for save post request"""

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

                if fb_api_name != 'usePolarisSaveMediaSaveMutation':
                    return

                variables_str = parsed.get('variables', ['{}'])[0]
                doc_id = parsed.get('doc_id', [''])[0]

                try:
                    variables = json.loads(variables_str)
                except:
                    self.base._log_to_file(f'SAVE_INVALID_VARS: {variables_str[:300]}', 'unknown')
                    return

                if 'media_id' not in variables:
                    self.base._log_to_file(f'SAVE_NO_MEDIA_ID: {json.dumps(variables)[:500]}', 'unknown')
                    return

                self.base.captured_data = {
                    'media_id': str(variables.get('media_id', '')),
                    'doc_id': doc_id,
                    'is_reel': self.is_reel,
                }

                self.ig.account.add_cli(f'Save post data captured: {self.base.captured_data}')

            except Exception as e:
                self.base._log_to_file(f'SAVE_LISTENER: {str(e)}', 'exception')

        self.base.listeners.append(on_response)
        self.ig.page.on('response', on_response)

    def _go_to_post_page(self):
        """Navigate to post page"""
        go_to_page(self.ig, self.order.target_link, 'Post Page')
        self.ig.pause(5000, 6000)

    def _check_post_errors(self):
        """Check for post/page errors"""
        if self.ig.is_visible_by_text('This account is private'):
            raise Exception('Account is private')

        if self.ig.is_visible_by_text("Post isn't available") or \
           self.ig.is_visible_by_text("The link may be broken") or \
           self.ig.is_visible_by_text("the profile may have been removed"):
            raise Exception("Post isn't available")

        if self.ig.is_visible_by_text("Sorry, this page isn't available") or \
           self.ig.is_visible_by_text("Page is not available") or \
           self.ig.is_visible_by_text("This page isn't available"):
            raise Exception("Page is not available")

        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise Exception("Page load issue - temporary error")

    def _dismiss_popup(self):
        """Dismiss any popups that might block interaction"""
        self.ig.pause(1000, 1200)

        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
                self.ig.pause(1000, 1500)
            except Exception as e:
                self.ig.account.add_cli(f'Dismiss popup error: {str(e)}')

    def _click_save_button(self):
        """Click the save button"""
        self.ig.account.add_cli("Attempting to save post...")

        # Check if already saved
        if self._is_saved():
            self.ig.account.add_cli("Post is already saved, unsaving first...")
            self._unsave_post()
            self.ig.pause(2000, 3000)

        # Try to save
        if not self._try_save():
            raise Exception("Failed to click save button")

        self.ig.pause(1500, 2500)

    def _try_save(self):
        """Try to click the save button"""
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
        """Unsave the post (click remove/unsave button)"""
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
        """Check if post is already saved"""
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
        """Verify that the post was saved successfully"""
        self.ig.pause(1000, 1500)

        if not self._is_saved():
            raise Exception("Post was not saved - verification failed")

        self.ig.account.add_cli("Post saved successfully")
