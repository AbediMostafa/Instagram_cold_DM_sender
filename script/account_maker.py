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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.90 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.59 Safari/537.36",
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

    def start_browser(self):

        # self.initialize_by_profile()
        self.initialize()
        self.go_to_instagram()
        self.allow_cookies()
        self.go_to_tmp_mail()
        self.page.bring_to_front()
        self.pause(2000, 2500)
        self.page.get_by_role("link", name="Sign up").click()
        self.pause(3000, 4000)
        self.no_account_can_create_handler()
        self.fill_user_props()
        self.pause(4000, 6000)
        self.fill_birthday_fields()
        self.pause(20000, 22000)
        self.confirm_code()
        self.pause(23000, 25000)
        self.suspended_account_handler()
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

    def go_to_instagram(self):
        retries = 3
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
        self.page1 = self.context.pages[0]
        self.page1.on("response", self.page1_response_fetcher)

        try:
            self.page1.goto("https://temp-mail.org/en/", wait_until="domcontentloaded", timeout=10000)
        except Exception as e:
            print(f"Error reading response: {str(e)}")

        if self.is_visible_by_text('Verify you are human') or self.is_visible_by_text(
                'temp-mail.org needs to review the security'):
            raise Exception('Verify you are human')


    def fill_user_props(self):
        self.page.get_by_label("Mobile Number or Email").press_sequentially(self.email, delay=30)
        self.pause(1000, 1200)
        self.page.get_by_label("Password").press_sequentially(self.password, delay=40)
        self.pause(1000, 1400)
        self.page.get_by_label("Full Name").press_sequentially(self.full_name, delay=20)
        self.pause(1000, 1400)
        self.page.get_by_label("Username").press_sequentially(self.username, delay=20, timeout=0)
        self.pause(1000, 2500)
        self.page.mouse.click(100, 200)
        self.pause(1000, 2500)

        while self.is_visible_by_text("This username isn't available"):
            print('Username is not available')
            delete('username', self.username)
            self.get_username()
            self.page.get_by_label("Username").fill("")
            self.page.get_by_label("Username").press_sequentially(self.username, delay=20, timeout=0)
            self.pause(3000, 3500)

        try:
            self.page.get_by_role("button", name="Sign up").click()
        except Exception as e:
            self.page.get_by_role("button", name="Next").click(timeout=3000)

    def fill_birthday_fields(self):
        # Define the range for the year to ensure the person is under 40 years old
        current_year = 2024
        min_year = current_year - 40  # 1984 for a 40-year-old
        max_year = current_year - 18  # 2006 for an 18-year-old

        # Randomly select values for Month, Day, and Year
        month = random.randint(1, 12)  # 1 to 12
        day = random.randint(1, 28)  # 1 to 28 (to avoid February issues)
        year = random.randint(min_year, max_year)

        self.page.select_option('select[title="Month:"]', value=str(month))
        self.pause(1000, 1800)
        self.page.select_option('select[title="Day:"]', value=str(day))
        self.pause(1000, 1800)
        self.page.select_option('select[title="Year:"]', value=str(year))
        self.pause(2000, 2800)

        try:
            self.page.get_by_role("button", name="Next").click(timeout=3000)
        except Exception as e:
            self.page.get_by_role("button", name="Sign up").click()

        self.pause(1000, 1800)

    def confirm_code(self):

        for _ in range(10):

            if self.code:
                break

            print('We are not still get the code')
            self.pause(2000, 3500)

        try:
            # First choice: Locate by aria-label
            self.page.fill('input[aria-label="Confirmation Code"]', self.code)
            print("Filled the input using 'aria-label'.")
        except Exception as e:
            print(f"Failed to fill using 'aria-label': {e}")
            self.page.fill('input[name="email_confirmation_code"]', self.code)

        self.pause(2000, 3500)

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
        proxy_details = get_proxy_details(self.proxy.ip)

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=f'C:\\Users\\Administrator\\Desktop\\account_maker\\browser_{self.proxy.id}',
            bypass_csp=True,
            permissions=["geolocation", "notifications"],
            geolocation={"longitude": proxy_details['longitude'], "latitude": proxy_details['latitude']},
            locale=proxy_details["locale"],
            timezone_id=proxy_details["timezone"],
            user_agent=get_random_user_agent(),
            viewport=give_a_good_resolution(),
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-dev-shm-usage"
            ],
            proxy={
                "server": f"http://{self.proxy.ip}:{self.proxy.port}",
                "username": self.proxy.username,
                "password": self.proxy.password
            },
            headless=False)

        self.page = self.context.new_page()
        self.page.on("response", self.page_response_fetcher)
        self.apply_stealth()

    def pause(self, min_ms, max_ms):
        self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    def allow_cookies(self):
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

    def apply_stealth(self):
        self.page.add_init_script("""
            const fpPromise = import('https://fpjscdn.net/v3/myuueG0YZE9rfx0ACJQj')
                .then(FingerprintJS => FingerprintJS.load({
                    region: "ap"
                }))

            fpPromise
                .then(fp => fp.get())
                .then(result => {
                    const visitorId = result.visitorId
                    console.log(visitorId)
                })
           """)

        self.page.add_init_script(r"""
               const fakeIP = '%s';

               Object.defineProperty(navigator, 'connection', {
                   value: { downlink: 10, effectiveType: '4g', rtt: 50, saveData: false },
               });

               const originalRTCPeerConnection = window.RTCPeerConnection;
               window.RTCPeerConnection = function (config) {
                   const pc = new originalRTCPeerConnection(config);
                   pc.addEventListener('icecandidate', event => {
                       if (event.candidate) {
                           const modifiedCandidate = event.candidate.candidate.replace(
                               /(?:[0-9]{1,3}\.){3}[0-9]{1,3}/g, fakeIP
                           );
                           Object.defineProperty(event.candidate, 'candidate', {
                               value: modifiedCandidate,
                           });
                       }
                   });
                   return pc;
               };
           """ % self.proxy.ip)

        self.page.add_init_script("""
                   navigator.webdriver = false
                   Object.defineProperty(navigator, 'webdriver', {
                       get: () => false
                   })
               """)

        self.page.add_init_script("""
            const originalIndexedDB = window.indexedDB;
            Object.defineProperty(window, 'indexedDB', {
                get: () => originalIndexedDB
            });
        """)

        self.page.add_init_script("""
            Object.defineProperty(window, 'localStorage', {
                get: () => ({
                    length: 0,
                    getItem: () => null,
                    setItem: () => {},
                    removeItem: () => {},
                    clear: () => {}
                })
            });

            Object.defineProperty(window, 'sessionStorage', {
                get: () => ({
                    length: 0,
                    getItem: () => null,
                    setItem: () => {},
                    removeItem: () => {},
                    clear: () => {}
                })
            });
        """)

        self.page.add_init_script("""
            Object.defineProperty(window.navigator, 'storage', {
                value: {
                    persisted: () => Promise.resolve(false)
                }
            });
        """)

        # Spoof plugins and mimeTypes
        self.page.add_init_script("""
               Object.defineProperty(navigator, 'plugins', {
                   get: () => [
                       { name: 'PDF Viewer', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                       { name: 'Chrome PDF Viewer', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                       { name: 'Microsoft Edge PDF Viewer', description: 'Portable Document Format', filename: 'internal-pdf-viewer' }
                   ]
               });
               Object.defineProperty(navigator, 'mimeTypes', {
                   get: () => [
                       { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                       { type: 'text/pdf', suffixes: 'pdf', description: 'Portable Document Format' }
                   ]
               });
           """)

        # Faking the languages array
        self.page.add_init_script("""
           Object.defineProperty(navigator, 'languages', {
               get: () => ['en-US', 'en']
           });
           """)

        # Spoof Media Devices
        self.page.add_init_script("""
               Object.defineProperty(navigator, 'mediaDevices', {
                   get: () => ({
                       enumerateDevices: () => Promise.resolve([
                           { kind: 'audioinput', label: 'Microphone', deviceId: 'default' },
                           { kind: 'videoinput', label: 'Webcam', deviceId: 'default' }
                       ])
                   })
               });
           """)

        # Faking the getBattery method
        self.page.add_init_script("""
           navigator.getBattery = () => Promise.resolve({
               charging: true,
               chargingTime: 0,
               dischargingTime: Infinity,
               level: 1
           });
           """)

        # Faking the permissions for notifications
        self.page.add_init_script("""
           const originalQuery = window.navigator.permissions.query;
           window.navigator.permissions.query = (parameters) => (
               parameters.name === 'notifications' ?
               Promise.resolve({ state: Notification.permission }) :
               originalQuery(parameters)
           );
           """)

        # Faking the WebGL Vendor and Renderer
        self.page.add_init_script("""
               const getParameter = WebGLRenderingContext.prototype.getParameter;
               WebGLRenderingContext.prototype.getParameter = function(parameter) {
                   if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                       return "Google Inc."; // Vendor value
                   }
                   if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                       return "ANGLE (NVIDIA GeForce RTX 2080 Direct3D11 vs_5_0 ps_5_0, D3D11)"; // Renderer value
                   }
                   return getParameter.call(this, parameter);
               };

               const getSupportedExtensions = WebGLRenderingContext.prototype.getSupportedExtensions;
               WebGLRenderingContext.prototype.getSupportedExtensions = function() {
                   return [
                       "EXT_texture_filter_anisotropic",
                       "EXT_color_buffer_half_float",
                       "WEBGL_debug_renderer_info",
                       "WEBGL_lose_context",
                       "EXT_blend_minmax",
                       "EXT_disjoint_timer_query",
                       "EXT_frag_depth",
                       "OES_element_index_uint",
                       "OES_fbo_render_mipmap",
                       "OES_standard_derivatives",
                       "OES_texture_float",
                       "OES_texture_float_linear",
                       "OES_texture_half_float",
                       "OES_texture_half_float_linear",
                       "OES_vertex_array_object",
                       "WEBGL_compressed_texture_s3tc",
                       "WEBGL_compressed_texture_s3tc_srgb"
                   ];
               };
           """)

        self.page.add_init_script("""
                Object.defineProperty(WebGLRenderingContext.prototype, 'UNMASKED_VENDOR_WEBGL', {
                    get: () => 'Google Inc.',
                });

                Object.defineProperty(WebGLRenderingContext.prototype, 'UNMASKED_RENDERER_WEBGL', {
                    get: () => 'ANGLE (NVIDIA GeForce RTX 2080 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                });
            """)

        # Faking the Media Codecs
        self.page.add_init_script("""
           const canPlayType = HTMLMediaElement.prototype.canPlayType;
           HTMLMediaElement.prototype.canPlayType = function(type) {
               if (type === 'audio/mpeg') return 'probably';
               if (type === 'audio/ogg') return 'probably';
               if (type === 'video/mp4') return 'probably';
               if (type === 'video/webm') return 'probably';
               return '';
           };
           """)

        # Faking the WebRTC IP leak protection
        self.page.add_init_script("""
           const getParameter = RTCPeerConnection.prototype.getParameters;
           RTCPeerConnection.prototype.getParameters = function() {
               return { iceServers: [] };
           };
           """)

        # Faking the Hardware Concurrency
        self.page.add_init_script("""
           Object.defineProperty(navigator, 'hardwareConcurrency', {
               get: () => 4
           });
           """)

        # Canvas spoofing
        self.page.add_init_script("""
               const originalGetContext = HTMLCanvasElement.prototype.getContext;
               HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                   const context = originalGetContext.call(this, type, attributes);
                   if (type === '2d') {
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
           """)

        self.page.add_init_script("""
                const originalGetContextAttributes = WebGLRenderingContext.prototype.getContextAttributes;
                WebGLRenderingContext.prototype.getContextAttributes = function() {
                    const attributes = originalGetContextAttributes.call(this);
                    attributes.antialias = true;
                    attributes.alpha = true;
                    attributes.depth = true;
                    attributes.stencil = false;
                    attributes.premultipliedAlpha = true;
                    attributes.preserveDrawingBuffer = false;
                    return attributes;
                };
            """)

        self.page.add_init_script("""
              Object.defineProperty(document, 'fonts', {
                  get: () => ({
                      add: () => {},
                      delete: () => {},
                      clear: () => {},
                      check: () => true,
                      load: () => Promise.resolve([]),
                      ready: Promise.resolve([])
                  })
              });
          """)

    def get_username(self):
        result = get_a('username')

        if result is None or not result.text:
            raise ValueError("No username available in the database.")

        self.username = result.text

        # we delete this username from database to don't use for another account
        # delete('username', self.username)
        print(f'Selected username: {self.username}')

    def suspended_account_handler(self):
        if self.is_visible_by_text('We suspended your account'):
            raise Exception('We suspended your account')

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
                created_at=tehran_now(),  # Set creation time
                updated_at=tehran_now()  # Set the updated time
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
    creator = AccountCreator(proxy=get_next_proxy())
    creator.start_browser()
    try:
        pass
    except Exception as e:
        print(str(e))

    finally:
        if creator:
            creator.clean_up()

    sleep(300)
