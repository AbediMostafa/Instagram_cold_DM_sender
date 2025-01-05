import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
import random
from dotenv import load_dotenv
import requests
import socket
from script.models.AccountHelper import *
from script.models.Proxy import Proxy
from script.models.Profile import Profile
from script.models.Tag import Tag
from script.models.Taggable import Taggable
from script.extra.helper import *
from script.models.Template import get_a, delete
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.hooks.CheckForAccountActionsHook import CheckForAccountActionsHook
import threading

load_dotenv()


def girst_proxy_with_less_accounts(exception_proxy_ids=None):
    from script.models.Proxy import Proxy
    from script.extra.adapters.SettingAdapter import SettingAdapter

    query = (Proxy
             .select(Proxy, Proxy.id, fn.COUNT(Account.id).alias('account_count'))
             .join(Account, JOIN.LEFT_OUTER)
             .where(Proxy.state == 'active'))

    if exception_proxy_ids:
        query = query.where(~Proxy.id.in_(exception_proxy_ids))

    return (query
            .group_by(Proxy.id)
            .having(fn.COUNT(Account.id) < SettingAdapter.max_account_for_one_proxy())
            .order_by(fn.Random())
            .first())


def use_proxy():
    load_dotenv()
    return os.getenv('HAVE_PROXY') == 'True'


def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        ip = response.json()['origin']
        return ip
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return None


def get_proxy_ip():
    load_dotenv()

    proxy_domain = os.getenv('PROXY_IP')

    try:
        proxy_ip = socket.gethostbyname(proxy_domain)
        print(f"The IP address of the proxy server is: {proxy_ip}")
        return proxy_ip

    except socket.gaierror as e:
        print(f"Error resolving the domain name: {e}")
        return None


def get_random_user_agent():
    import random

    user_agents = [
        # Android Devices
        "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",

        # iOS Devices
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",

        # General Mobile Chrome
        "Mozilla/5.0 (Linux; Android 9; SM-J737T1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 8.1.0; Redmi Note 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",

        # General Mobile Firefox
        "Mozilla/5.0 (Android 11; Mobile; rv:94.0) Gecko/94.0 Firefox/94.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/96.0 Mobile/15E148 Safari/605.1.15",
    ]

    return random.choice(user_agents)


def give_a_good_resolution():
    resolutions = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1280, 'height': 1024},
    ]

    return random.choice(resolutions)


# Fetch geolocation, timezone, and locale information from the proxy IP
def get_proxy_details(proxy_ip):
    try:
        response = requests.get(f'https://freeipapi.com/api/json/{proxy_ip}')
        data = response.json()

        # Extract geolocation (latitude, longitude)
        # loc = data['loc'].split(',')
        latitude = data['latitude']
        longitude = data['longitude']

        # Extract timezone and country if available
        timezone = data['timeZones'][0]  # Default to Los Angeles if not available
        country = data.get('countryCode', 'US')  # Default to US if country info isn't available

        # Default language based on country (you can customize this mapping as needed)
        language_mapping = {
            'US': 'en',
            'FR': 'fr',
            'DE': 'de',
        }

        # Set the language based on the country (default to 'en' for unknown countries)
        language = language_mapping.get(country, 'en')

        # Construct the locale (e.g., en-US, fr-FR)
        locale = f"{language.lower()}-{country.upper()}"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "locale": locale
        }

    except Exception as e:
        print(f"Error fetching proxy details: {e}")

        return {
            "latitude": None,
            "longitude": None,
            "timezone": None,
            "locale": None
        }


class AccountCreator:
    account = None
    proxy = None
    email = None
    code = None
    password = None
    username = None
    full_name = 'Edward Air'
    browser_ig = None
    month = None
    day = None
    year = None

    def __init__(self, profile=None, proxy=None):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.page1 = None
        self.profile = profile
        self.proxy = proxy

        self.password = generate_random_word()
        self.get_username()
        self.get_birth_day()

    def start_browser(self):

        # self.initialize_by_profile()
        self.initialize()
        self.go_to_instagram()
        self.allow_cookies()
        self.go_to_tmp_mail()
        self.page.bring_to_front()
        self.click_on_sign_up()
        self.pause(3000, 4000)
        self.account_cant_be_created_here()
        self.first_method() if self.is_visible_by_text("What's your mobile number") else self.second_method()

        self.pause(4000, 6000)
        self.something_went_wrong_creating_your_account_handler()
        # Sorry, something went wrong creating your account. Please try again soon.
        self.save_info()
        self.pause(2000, 3000)
        self.create_account()
        self.page.reload()
        self.pause(10000, 12000)
        self.save_session()
        delete('username', self.username)
        print(f'Username deleted successfully: {self.username}')
        self.follow_suggested()

        try:

            CheckForAccountActionsHook(self.account)
            self.browser_ig = BasePlaywright(self.account)
            self.account.set_state('processing', 'app_state')
            BrowserChangeAvatarEvent(self.browser_ig).fire()

        except Exception as e:
            print(str(e))

    def click_on_sign_up(self):
        print('Clicking on sign up ...')

        try:
            self.page.locator("div.x9f619.xjbqb8w.x1rg5ohu.x168nmei.x13lgxp2 button:nth-of-type(2)").first.click(
                timeout=3000)
        except Exception as e:
            print(str(e))
            self.page.get_by_role("link", name="Sign up for Instagram").click(timeout=3000)

    def next(self):
        self.pause(3000, 4000)

        try:
            self.page.get_by_label("Next").click(timeout=3000)
        except Exception as e:
            self.page.get_by_role("button", name="Next").click(timeout=3000)

        self.pause(3000, 4000)

    def account_cant_be_created_here(self):
        if self.is_visible_by_text('In response to a new law in your area') or self.is_visible_by_text(
                'an account can’t be created here') or self.is_visible_by_text(
            'You can create your account by going to the Instagram app') or self.is_visible_by_text(
            'Go to the Instagram app to create an account'):
            raise Exception('In response to a new law in your area, an account can’t be created here')

    def first_method(self):
        print('implementing first method  ...')
        print('Filling email ...')

        self.page.get_by_label("Sign up with email").click(timeout=3000)
        self.page.get_by_label("Email", exact=True).press_sequentially(self.email, delay=100, timeout=7000)
        self.pause(2000, 3000)
        self.next()

        for _ in range(10):
            if self.code:
                break

            print('We are not still get the code')
            self.pause(2000, 3500)

        print('Filling Confirmation code ...')
        self.page.get_by_label("Confirmation code", exact=True).fill(self.code)
        self.next()

        self.page.get_by_label("Password", exact=True).press_sequentially(self.password, delay=100, timeout=3000)
        self.next()

        birth_day = f'{self.month}{self.day}{self.year}'
        self.page.locator("input[type='date'][aria-label*='Birthday']").press_sequentially(birth_day, delay=200,
                                                                                           timeout=3000)
        self.next()

        self.page.get_by_label("Full name").fill(self.full_name)
        self.next()

        self.page.get_by_label("Username", exact=True).fill("")
        self.page.get_by_label("Username", exact=True).press_sequentially(self.username, delay=100, timeout=0)
        self.pause(2000, 3500)
        self.next()

        self.page.get_by_label("I agree").click(timeout=3000)

        if self.is_visible_by_text("sorry, but something went wrong"):
            raise Exception('Sorry, but something went wrong')

    def second_method(self):
        self.fill_email()
        self.pause(4000, 6000)
        self.having_trouble_verifying_your_email_handler()
        self.confirm_code()
        self.pause(6000, 8000)
        self.having_trouble_verifying_your_confirmation_code()
        self.fill_name_password()
        self.pause(4000, 6000)
        self.fill_birthday_fields()
        self.fill_username()

    def go_to_instagram(self):
        retries = 3
        print('Go to Instagram ...')
        for attempt in range(retries):
            try:
                self.page.goto('https://www.instagram.com/', timeout=200000)
                break
            except Exception as e:
                if attempt == retries - 1:
                    raise e

    def page1_response_fetcher(self, response):
        # https: // web2.temp - mail.org / messages
        if "web2.temp-mail.org/mailbox" in response.url:
            try:
                json_data = response.json()
                self.email = json_data['mailbox']
                print(f"Response from API: {self.email}")
            except Exception as e:
                print(f"Error reading response: {e}")

        if "web2.temp-mail.org/messages" in response.url:
            try:
                json_data = response.json()

                if not json_data['messages']: return

                subject = json_data['messages'][0]['subject']

                print(f"Subject: {subject}")

                # Regular expression to match a 6-digit number
                match = re.search(r'\b\d{6}\b', subject)

                # Extract and print the code if found
                if match:
                    self.code = match.group()
                    print(f"Extracted code: {self.code}")
                else:
                    print("No code found.")

            except Exception as e:
                print(f"Error reading response: {e}")

    def page_response_fetcher(self, response):
        if "api/v1/web/accounts/web_create_ajax/attempt" in response.url:
            if response.status == 429:
                raise Exception("429 Too many requests")

    def go_to_tmp_mail(self):
        print('Going to tmp mail')
        self.context1 = self.browser.new_context()
        self.page1 = self.context1.new_page()
        self.page1.on("response", self.page1_response_fetcher)

        try:
            self.page1.goto("https://temp-mail.org/en/", wait_until="domcontentloaded", timeout=10000)
        except Exception as e:
            print(f"Error reading response: {str(e)}")

        if self.is_visible_by_text('Verify you are human') or self.is_visible_by_text(
                'temp-mail.org needs to review the security'):
            raise Exception('Verify you are human')

    def fill_email(self):

        try:
            self.page.get_by_role("switch", name="Email").click(timeout=3000)

        except Exception as e:
            print(f"Error clicking on Email: {str(e)}")
            self.page.selector("span[role='switch'][aria-checked='true']:has-text('Email')").click(timeout=3000)

        self.pause(1500, 2000)

        try:
            self.page.get_by_placeholder("Email Address").press_sequentially(self.email, delay=100, timeout=0)
        except Exception as e:
            print(f"Error clicking on Email: {str(e)}")

        self.next()

    def having_trouble_verifying_your_email_handler(self):
        if self.is_visible_by_text('having trouble verifying your email') or self.is_visible_by_text(
                'Please try again later'):
            raise Exception('having trouble verifying your email')

    def fill_birthday_fields(self):

        self.page.select_option('select[title="Month:"]', value=str(self.month))
        self.pause(1000, 1800)
        self.page.select_option('select[title="Day:"]', value=str(self.day))
        self.pause(1000, 1800)
        self.page.select_option('select[title="Year:"]', value=str(self.year))
        self.pause(2000, 2800)

        try:
            self.page.get_by_role("button", name="Next").click(timeout=3000)
        except Exception as e:
            self.page.get_by_role("button", name="Sign up").click()

        self.pause(1000, 1800)

    def fill_username(self):
        # Welcome to Instagram, geconat660
        # Find people to follow and start sharing photos. You can change your username anytime.

        if self.is_visible_by_text('Welcome to Instagram') or self.is_visible_by_text('Find people to follow and start sharing photos'):
            if self.is_visible_by_text('Change username'):
                try:
                    self.page.get_by_role("button", name="Change username").click(timeout=3000)
                except Exception as e:
                    print(str(e))
                    self.page.locator('div._ae03 button._ae06._acan._acao._acas._aj1-._ap30').click()

        self.pause(1000, 1800)

        try:
            self.page.get_by_placeholder("Username").fill("")
            self.page.get_by_placeholder("Username").press_sequentially(self.email, delay=100, timeout=7000)
        except Exception as e:
            print(str(e))
            self.page.locator("label._aa48 input[aria-label='Username']").fill("")
            self.page.locator("label._aa48 input[aria-label='Username']").press_sequentially(self.email, delay=100, timeout=7000)

        self.pause(2000, 3000)

        self.page.get_by_role("button", name="Next").click(timeout=3000)

    def confirm_code(self):

        for _ in range(10):
            if self.code:
                break

            print('We are not still get the code')
            self.pause(2000, 3500)

        try:
            self.page.get_by_placeholder("Confirmation Code").fill(self.code)
        except Exception as e:
            raise Exception(f'Problem Filling confirmation code .. {str(e)} ')

        self.pause(2000, 3500)

        self.page.get_by_role("button", name="Next").click(timeout=3000)

        self.pause(2000, 3500)

    def having_trouble_verifying_your_confirmation_code(self):
        if self.is_visible_by_text('having trouble verifying your confirmation code') or self.is_visible_by_text(
                'Please try again later'):
            raise Exception('having trouble verifying your confirmation code')

    def fill_name_password(self):

        self.page.get_by_placeholder("Full Name").fill(self.full_name, timeout=3000)
        self.pause(2000, 2500)
        self.page.get_by_placeholder("Password").fill(self.password, timeout=3000)
        self.pause(2000, 2500)
        self.page.get_by_role("button", name="Next").click(timeout=3000)

    def initialize_by_profile(self):

        self.playwright = sync_playwright().start()
        mlx_url = get_antidetect_endpoint_url(self.profile.profile_id)
        self.browser = self.playwright.chromium.connect_over_cdp(mlx_url)

        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.on("response", self.page_response_fetcher)

    def initialize(self):
        print('Initializing playwright...')
        self.playwright = sync_playwright().start()
        # self.proxy = girst_proxy_with_less_accounts()

        print(self.proxy.id)

        self.browser = self.playwright.chromium.launch(
            proxy={
                # "server": f"http://168.119.244.147:13957",
                "server": f"http://{self.proxy.ip}:{self.proxy.port}",
                # "username": 'support191929',
                "username": self.proxy.username,
                # "password": "jbrjgud123dptzr"
                "password": self.proxy.password
            },
            timeout=120000,
            headless=False)

        self.randomize_browser_context()
        self.page = self.context.new_page()
        self.page.on("response", self.page_response_fetcher)

        self.apply_stealth()

    def pause(self, min_ms, max_ms):
        self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    def allow_cookies(self):
        print('Allowing cookies ...')

        for i in range(3):
            try:
                try:
                    self.page.locator('button', has_text='Allow All Cookies').click(timeout=1500)
                except:
                    self.page.locator('button', has_text='Allow all cookies').click(timeout=1500)

                return True
            except Exception as e:
                pass

    def is_visible_by_text(self, text):
        try:
            return self.page.locator(f"text={text}").is_visible()
        except Exception as e:
            return False

    def spoof_canvas(self):
        self.page.add_init_script("""
        // Intercept and modify the canvas fingerprinting attempt
        HTMLCanvasElement.prototype.getContext = (function(original) {
            return function(type, attributes) {
                const context = original.call(this, type, attributes);
                if (type === "2d") {
                    const originalGetImageData = context.getImageData;
                    context.getImageData = function(x, y, width, height) {
                        const imageData = originalGetImageData.call(this, x, y, width, height);
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] = imageData.data[i] ^ 255; // Invert color
                        }
                        return imageData;
                    };
                }
                return context;
            };
        })(HTMLCanvasElement.prototype.getContext);
        """)

    def spoof_webgl(self):
        self.page.add_init_script("""
        // Spoof the WebGL parameters for fingerprinting evasion
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                return "MyCustomVendor";
            }
            if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                return "MyCustomRenderer";
            }
            return getParameter.call(this, parameter);
        };
        """)

    def keep_tab_active(self):
        import time
        """
        Periodically sends a no-op JavaScript command to keep the tab active.
        :param page: The Playwright page object.
        :param interval: Time interval in seconds between keep-alive signals.
        """
        while True:
            try:
                self.page.evaluate("() => console.log('Keeping tab active')")
            except Exception as e:
                print(f"Error in keep-alive: {e}")
                break
            time.sleep(2)

    def randomize_browser_context(self):
        proxy_details = get_proxy_details(self.proxy.ip)

        print(proxy_details)

        self.context = self.browser.new_context(
            geolocation={"longitude": proxy_details['longitude'], "latitude": proxy_details['latitude']} if
            proxy_details['longitude'] else None,
            permissions=["geolocation", 'notifications'],
            viewport=give_a_good_resolution(),
            locale=proxy_details["locale"],
            timezone_id=proxy_details["timezone"],
            user_agent=get_random_user_agent(),
            bypass_csp=True
        )

    def apply_stealth(self):
        print("Apply some browser stealth ...")

        self.page.add_init_script("""
                   navigator.webdriver = false
                   Object.defineProperty(navigator, 'webdriver', {
                       get: () => false
                   })
               """)

        # Adding fake Chrome object
        # self.page.add_init_script("""
        #    window.chrome = {
        #        runtime: {}
        #    };
        #    """)
        #
        # # Faking the plugins array
        # self.page.add_init_script("""
        #    Object.defineProperty(navigator, 'plugins', {
        #        get: () => [1, 2, 3]
        #    });
        #    """)
        #
        # # Faking the permissions for notifications
        # self.page.add_init_script("""
        #    const originalQuery = window.navigator.permissions.query;
        #    window.navigator.permissions.query = (parameters) => (
        #        parameters.name === 'notifications' ?
        #        Promise.resolve({ state: Notification.permission }) :
        #        originalQuery(parameters)
        #    );
        #    """)
        #
        # # Faking the WebGL Vendor and Renderer
        # self.page.add_init_script("""
        #    const getParameter = WebGLRenderingContext.prototype.getParameter;
        #    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        #        if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
        #            return 'Intel Inc.';
        #        }
        #        if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
        #            return 'Intel Iris OpenGL Engine';
        #        }
        #        return getParameter(parameter);
        #    };
        #    """)
        #
        # # Faking the Media Codecs
        # self.page.add_init_script("""
        #    const canPlayType = HTMLMediaElement.prototype.canPlayType;
        #    HTMLMediaElement.prototype.canPlayType = function(type) {
        #        if (type === 'audio/mpeg') return 'probably';
        #        if (type === 'audio/ogg') return 'probably';
        #        if (type === 'video/mp4') return 'probably';
        #        if (type === 'video/webm') return 'probably';
        #        return '';
        #    };
        #    """)
        #
        # # Faking the WebRTC IP leak protection
        # self.page.add_init_script("""
        #    const getParameter = RTCPeerConnection.prototype.getParameters;
        #    RTCPeerConnection.prototype.getParameters = function() {
        #        return { iceServers: [] };
        #    };
        #    """)
        #
        # # Faking the Hardware Concurrency
        # self.page.add_init_script("""
        #    Object.defineProperty(navigator, 'hardwareConcurrency', {
        #        get: () => 4
        #    });
        #    """)
        #
        # self.page.add_init_script("""
        #        // Intercept and modify the canvas fingerprinting attempt
        #        HTMLCanvasElement.prototype.getContext = (function(original) {
        #            return function(type, attributes) {
        #                const context = original.call(this, type, attributes);
        #                if (type === "2d") {
        #                    const originalGetImageData = context.getImageData;
        #                    context.getImageData = function(x, y, width, height) {
        #                        const imageData = originalGetImageData.call(this, x, y, width, height);
        #                        for (let i = 0; i < imageData.data.length; i += 4) {
        #                            imageData.data[i] = imageData.data[i] ^ 255; // Invert color
        #                        }
        #                        return imageData;
        #                    };
        #                }
        #                return context;
        #            };
        #        })(HTMLCanvasElement.prototype.getContext);
        #        """)
        #
        # self.page.add_init_script("""
        #         // Spoof the WebGL parameters for fingerprinting evasion
        #         const getParameter = WebGLRenderingContext.prototype.getParameter;
        #         WebGLRenderingContext.prototype.getParameter = function(parameter) {
        #             if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
        #                 return "MyCustomVendor";
        #             }
        #             if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
        #                 return "MyCustomRenderer";
        #             }
        #             return getParameter.call(this, parameter);
        #         };
        #         """)

    def get_username(self):
        result = get_a('username')

        if result is None or not result.text:
            raise ValueError("No username available in the database.")

        self.username = result.text

        # we delete this username from database to don't use for another account
        # delete('username', self.username)
        print(f'Selected username: {self.username}')

    def get_birth_day(self):
        current_year = 2024
        min_year = current_year - 40  # 1984 for a 40-year-old
        max_year = current_year - 18  # 2006 for an 18-year-old

        # Randomly select values for Month, Day, and Year
        self.month = random.randint(1, 12)  # 1 to 12
        self.day = random.randint(1, 28)  # 1 to 28 (to avoid February issues)
        self.year = random.randint(min_year, max_year)

    def suspended_account_handler(self):
        if self.is_visible_by_text('We suspended your account'):
            raise Exception('We suspended your account')

    def something_went_wrong_creating_your_account_handler(self):
        if self.is_visible_by_text('something went wrong creating your account'):
            raise Exception('something went wrong creating your account')

    def no_account_can_create_handler(self):
        if self.is_visible_by_text('New accounts can only be created on phones'):
            raise Exception('New accounts can only be created on phones')

    def open_proxy_ip(self):
        if self.is_visible_by_text('The IP address you are using has been flagged as an open proxy'):
            raise Exception('The IP address you are using has been flagged as an open proxy')

    def save_info(self):
        try:
            self.page.get_by_role("button", name="Save info", exact=True).click(timeout=3500)
        except:
            pass

    def create_account(self):
        try:
            # Create the account with the given details
            self.account = Account.create(
                proxy=self.proxy,  # Associate with the proxy
                username=self.username,  # Set the username
                password=self.password,  # Set the password
                name=self.full_name,  # Set the name
                username_changed=1,  # Mark as username changed
                created_at=datetime.now(),  # Set creation time
                updated_at=datetime.now()  # Set the updated time
            )

            automation_tag, created = Tag.get_or_create(title='automation')

            Taggable.create(
                tag=automation_tag,
                taggable_id=self.account.id,
                taggable_type=Taggable.get_taggable_class('Account')  # Use the corresponding model mapping
            )

            print(f"Account created successfully with username: {self.account.username}")
        except Exception as e:
            print(f"Error creating account: {str(e)}")
            return None

    def save_session(self):

        storage_state = self.page.context.storage_state()
        storage_state_json = json.dumps(storage_state)
        self.account.save_session(storage_state_json)

    def follow_suggested(self):
        if self.is_visible_by_text('Find friends and accounts you like'):
            print('Find friends and accounts you like')

            for _ in range(2):
                try:
                    self.page.get_by_role("button", name="Next").first.click(timeout=3000)
                except Exception as e:
                    print(str(e))

                pause(3000, 5000)

    def clean_up(self):
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()


#
# while True:
#     try:
#         creator = AccountCreator()
#         creator.start_browser()
#     except Exception as e:
#         print(str(e))
#
#     finally:
#         if creator:
#             creator.clean_up()

while True:
    try:
        creator = AccountCreator(proxy=get_next_proxy())
        creator.start_browser()
    except Exception as e:
        print(str(e))

    finally:
        sleep(100000)
        if creator:
            creator.clean_up()

    sleep(300)
