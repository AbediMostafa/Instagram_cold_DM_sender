from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random
import traceback
from script.extra.helper import get_random_user_agent
from script.extra.instagram.browser.InstagramSuspensionHandlerMixin import InstagramSuspensionHandlerMixin
from script.extra.instagram.browser.InstagramButtonHandlerMixin import InstagramButtonHandlerMixin
from script.extra.exceptions import *
import json


class BasePlaywright(InstagramButtonHandlerMixin, InstagramSuspensionHandlerMixin):

    def __init__(self, account):
        self.account = account
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.start_browser()

    def start_browser(self):

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            proxy={
                "server": f"http://{self.account.proxy.ip}:{self.account.proxy.port}",
                "username": self.account.proxy.username,
                "password": self.account.proxy.password
            },
            headless=False)
        self.randomize_browser_context()
        self.page = self.context.new_page()
        self.apply_stealth()

    def cleanup(self):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def goto(self, url, timeout=30000):
        try:
            self.page.goto(url, timeout=timeout)
        except PlaywrightTimeoutError:
            self.handle_exception(f'Timeout while trying to go to {url}')

    def pause(self, min_ms, max_ms):
        self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    def allow_cookies(self):
        self.account.add_cli(f'Trying to allow cookies ...')

        for i in range(7):
            try:
                try:
                    self.page.locator('button', has_text='Allow All Cookies').click(timeout=1500)
                except:
                    self.page.locator('button', has_text='Allow all cookies').click(timeout=1500)

                self.account.add_cli(f'Clicked on allow cookies')
                return True
            except Exception as e:
                pass

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

    def two_factor_authentication_process(self):

        self.page.get_by_label("Security Code").press_sequentially(self.account.get_verification_code(), delay=100)
        # self.pause(1000, 1800)

        self.page.get_by_role("button", name="Confirm").click()
        self.account.add_cli('2FA confirm clicked')

    def something_went_wrong(self):
        if self.is_visible_by_text("There's an issue and the page could not be loaded"):
            self.account.add_cli("There's an issue and the page could not be loaded")
            self.page.get_by_role("button", name="Reload page").click()
            return True

        return False

    def unusual_login_detected(self):
        if self.is_visible_by_text('We Detected An Unusual Login') or self.is_visible_by_text(
                "We've detected an unusual login attempt"):
            self.account.add_cli('Unusual Login Detected')
            self.page.get_by_role("button", name="This Was Me").click()
            return True

        return False

    def not_connect_to_the_internet(self):
        if self.is_visible_by_text("We couldn't connect to Instagram"):
            raise NotConnectedToTheInternetError(
                "We couldn't connect to Instagram. Make sure you're connected to the internet and try again.")

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

    def randomize_browser_context(self):
        screen_width = random.choice([1920, 1366, 1440, 1536])
        screen_height = random.choice([1080, 768, 900, 864])
        storage_state = self.account.web_session

        try:
            decoded = json.loads(storage_state)
            if isinstance(decoded, str):
                decoded = json.loads(decoded)

        except Exception as e:
            decoded = {}

        self.context = self.browser.new_context(
            # viewport={'width': screen_width, 'height': screen_height}, 
            locale=random.choice(['en-US', 'en-GB']),
            timezone_id=random.choice(['UTC', 'America/New_York', 'Europe/Berlin']),
            user_agent=get_random_user_agent(),
            storage_state=decoded
        )

    def password_is_incorrect_handler(self):
        if self.is_visible_by_text('your password was incorrect'):
            self.account.set_state(state='suspended', log='Your password was incorrect')
            raise YourPasswordWasIncorrectError('Your password was incorrect')

    def problem_logging_in_handler(self):
        if self.is_visible_by_text('was a problem logging you into Instagram'):
            raise ProblemLogingYouError('There was a problem logging you into Instagram .please try again soon')

    def suspended_account_handler(self):
        if self.is_visible_by_text('We suspended your account'):
            raise AccountSuspendedError('We suspended your account')

    def suspect_automate_behavior_handler(self):

        if self.is_visible_by_text('suspect automated behavior') or self.is_visible_by_text(
                'suspect automated behaviour') or self.is_visible_by_text(
            'To prevent your account from being temporarily restricted or permanently disabled'):

            try:
                self.account.add_cli('We suspect automated behavior on your account')
                self.page.get_by_role("button", name='Dismiss').click(timeout=5000)
                return True

            except Exception as e:
                raise Exception(f'Problem clicking on Dismiss:{str(e)}')

        return False

    def help_us_confirm_its_you_handler(self):
        if self.is_visible_by_text('Help us confirm it') or self.is_visible_by_text("Help us confirm that it's you"):
            raise HelpUsConfirmItsYouError("Help us confirm it's you")

    def feedback_required(self):
        if self.is_visible_by_text('feedback_required') or self.is_visible_by_text("feedback required"):
            raise FeedbackRequired("feedback required")

    def save_info(self):
        try:
            self.account.add_cli('Saving information ...')
            self.page.get_by_role("button", name="Save info", exact=True).click(timeout=3500)
            self.pause(5000, 6000)
        except:
            self.account.add_cli("Save info doesn't exists")
            pass

    def turn_on_notif(self):
        self.account.add_cli('Turn on notification...')
        try:
            self.page.get_by_role("button", name="Turn On", exact=True).click(timeout=3500)
            self.pause(5000, 6000)
        except:
            self.account.add_cli("Turn On doesn't exists")
            pass

    def save_session(self):

        storage_state = self.page.context.storage_state()
        storage_state_json = json.dumps(storage_state)
        self.account.save_session(storage_state_json)

    def apply_stealth(self):
        self.page.add_init_script("""
           Object.defineProperty(navigator, 'webdriver', {
               get: () => undefined
           });
           """)

        # Adding fake Chrome object
        self.page.add_init_script("""
           window.chrome = {
               runtime: {}
           };
           """)

        # Faking the plugins array
        self.page.add_init_script("""
           Object.defineProperty(navigator, 'plugins', {
               get: () => [1, 2, 3]
           });
           """)

        # Faking the languages array
        self.page.add_init_script("""
           Object.defineProperty(navigator, 'languages', {
               get: () => ['en-US', 'en']
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
                   return 'Intel Inc.';
               }
               if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                   return 'Intel Iris OpenGL Engine';
               }
               return getParameter(parameter);
           };
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
