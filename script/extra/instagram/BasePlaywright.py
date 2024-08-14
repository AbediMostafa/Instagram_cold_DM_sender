from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random
import traceback


class BasePlaywright:
    def __init__(self, account):
        self.account = account
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.start_browser()

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def goto(self, url, timeout=30000):
        try:
            self.page.goto(url, timeout=timeout)
        except PlaywrightTimeoutError:
            self.handle_exception(f'Timeout while trying to go to {url}')

    def pause(self, min_ms, max_ms):
        self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    def allow_cookies(self):
        try:
            self.page.locator('button', has_text='Allow All Cookies').click()
        except Exception as e:
            self.account.add_cli('Cookies button not found or could not be clicked')

    def is_visible_by_text(self, text):
        try:
            return self.page.locator(f"text={text}").is_visible()
        except Exception as e:
            return False

    def fill_property(self, property_name, value):
        try:
            input_selector = f"input[name='{property_name}']"
            self.page.fill(input_selector, value)
        except Exception as e:
            self.handle_exception(f'Error filling property {property_name} with value {value}: {str(e)}')

    def click_on_profile_attribute(self, attribute_name):
        try:
            self.page.locator(f"text={attribute_name}").click()
        except Exception as e:
            self.handle_exception(f'Error clicking on profile attribute {attribute_name}: {str(e)}')

    def click_by_role(self, role_name):
        try:
            self.page.locator(f"button[name='{role_name}']").click()
        except Exception as e:
            self.handle_exception(f'Error clicking button with role {role_name}: {str(e)}')

    def handle_exception(self, reason, _type='raise'):
        self.account.add_cli(reason)
        self.account.add_log(traceback.format_exc())

        if _type == 'raise':
            raise Exception(reason)

    def close_browser(self):
        self.browser.close()
        self.playwright.stop()
