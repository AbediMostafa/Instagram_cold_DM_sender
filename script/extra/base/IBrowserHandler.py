from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from script.models.Setting import Setting
from script.models.AccountHelper import get_storage_state
import json


class IBrowserHandler:
    storage_state = None
    ws_endpoint = None
    profile_id = None
    playwright = None
    browser = None
    context = None
    page = None
    server_type = 'fit'

    def __init__(self, account):
        self.account = account
        self.server_type = Setting.get_value('server_type_by_account_count', 'fit')
        self.playwright = sync_playwright().start()

    def start_browser(self):

        try:
            self.browser = self.playwright.chromium.connect_over_cdp(self.ws_endpoint)
        except Exception as e:
            self.account.add_cli(f'Problem opening chromium over cdp: {str(e)}')
            self.browser.close()

        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]

        # # If we run more accounts than our profiles should clear cookies to be ready for next account
        # if self.server_type == 'more':
        #
        # if not get_storage_state(self.account):
        #     self.context.clear_cookies()
        #
        # self.context.add_cookies(self.storage_state.get("cookies", []))

    def cleanup(self):

        if self.browser:
            try:
                self.account.add_cli('Closing Browser ...')
                self.browser.close()
            except Exception as e:
                self.account.add_cli(f'Problem closing browser : {str(e)}')

        if self.playwright:
            try:
                self.account.add_cli('Stopping Playwright ...')
                self.playwright.stop()
            except Exception as e:
                self.account.add_cli(f'Problem stopping playwright : {str(e)}')

    def get_browser(self):
        return self.browser

    def get_context(self):
        return self.context

    def get_page(self):
        return self.page
