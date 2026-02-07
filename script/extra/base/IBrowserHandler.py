from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from script.models.Setting import Setting
from script.models.AccountHelper import get_storage_state
import json
import os, hashlib, requests, time

CACHE_DIR = r'C:\Users\admin\Desktop\tmp\cache'


def cache_key(url):
    # include querystring so different tokens are separate
    h = hashlib.sha256(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, h)


def fetch_and_save(url):
    path = cache_key(url)

    if os.path.exists(path):
        return open(path, 'rb').read() 
    r = requests.get(url, timeout=20)
    if r.status_code == 200:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content
    return None


class IBrowserHandler:
    storage_state = None
    ws_endpoint = None
    profile_id = None
    playwright = None
    browser = None
    context = None
    page = None

    def __init__(self, account):
        self.account = account
        self.playwright = sync_playwright().start()

    def start_browser(self):

        try:
            self.browser = self.playwright.chromium.connect_over_cdp(self.ws_endpoint)
        except Exception as e:
            self.account.add_cli(f'Problem opening chromium over cdp: {str(e)}')
            self.browser.close()

        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]

        # self.page.route("**/*", self.handle_route)

    def handle_route(self, route, request):
        url = request.url

        blocked_domains = [
            "instagram.fath3-3.fna.fbcdn",
        ]

        if any(domain in url for domain in blocked_domains):
            return route.abort()

        if "scontent-" in url and ".cdninstagram.com" in url:
            return route.abort()

        if request.resource_type in ['image', 'media']:
            return route.abort()

        request = route.request
        url = request.url

        if 'instagram' in url and url.endswith(('.js', '.css', '.png', '.jpg', '.json', '.wasm')):
            data = fetch_and_save(url)
            if data:
                route.fulfill(
                    status=200,
                    headers={'content-type': request.headers.get('accept', 'application/octet-stream')},
                    body=data
                )
                return

        # Cache full HTML pages
        return route.continue_()

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

    def clear_storage(self):
        # self.context.clear_cookies()
        self.page.evaluate("""() => {
            localStorage.clear();
            sessionStorage.clear();
            indexedDB.databases().then(dbs => {
                dbs.forEach(db => indexedDB.deleteDatabase(db.name));
            });
        }""")

    def get_browser(self):
        return self.browser

    def get_context(self):
        return self.context

    def get_page(self):
        return self.page
