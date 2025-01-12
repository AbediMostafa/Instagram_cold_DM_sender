from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import random
import traceback
from script.extra.helper import *
from script.extra.instagram.browser.InstagramSuspensionHandlerMixin import InstagramSuspensionHandlerMixin
from script.extra.instagram.browser.InstagramButtonHandlerMixin import InstagramButtonHandlerMixin
from script.extra.exceptions import *
from script.extra.events.browser_events.ApplyStealth import ApplyStealth
from script.extra.modules.multilogin.Requests import Requests
import json


# Your account has been disabled
class BasePlaywright(InstagramButtonHandlerMixin, InstagramSuspensionHandlerMixin):
    resolution = None
    apply_stealth = None

    def __init__(self, account):
        self.account = account
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.mlx_url = None
        self.profile_id = None

    def start_browser(self):

        self.playwright = sync_playwright().start()
        self.run_with_profile() if self.account.profile else self.run_with_proxy()
        # self.run_with_proxy()

        return self

    def run_with_profile(self):
        self.profile_id = self.account.profile.profile_id

        self.mlx_url = Requests().get_mlx_endpoint_url(self.profile_id)
        self.browser = self.playwright.chromium.connect_over_cdp(self.mlx_url)
        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]

    def run_with_proxy(self):
        if not self.account.proxy:
            self.account.get_proxy()

        self.resolution = give_a_good_resolution()
        proxy_details = get_proxy_details(self.account.proxy.ip)
        locale = proxy_details["locale"],
        #     timezone_id=proxy_details["timezone"],

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=f'C:\\Users\\Administrator\\Desktop\\browser_data\\browser_{self.account.id}',
            bypass_csp=True,
            user_agent=get_random_user_agent(),
            permissions=["geolocation", "notifications"],
            geolocation={"longitude": proxy_details['longitude'], "latitude": proxy_details['latitude']},
            locale=proxy_details["locale"],
            timezone_id=proxy_details["timezone"],
            viewport={'width': self.account.screen_resolution.width, 'height': self.account.screen_resolution.height},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-dev-shm-usage"
            ],
            proxy={
                "server": f"http://{self.account.proxy.ip}:{self.account.proxy.port}",
                "username": self.account.proxy.username,
                "password": self.account.proxy.password
            },
            headless=False)

        self.randomize_browser_context()
        self.page = self.context.pages[0]

        # Apply stealth
        self.apply_stealth = ApplyStealth(self.account, self.page)
        self.apply_stealth.init()

        # self.context.route("**/*", self.intercept_request)

    def intercept_request(self, route, request):
        # Generate spoofed Sec-CH-UA headers
        spoofed_headers = {
            "Sec-CH-UA": '"Not_A;Brand";v="99", "Chromium";v="97", "Google Chrome";v="97"',
            "Sec-CH-UA-Platform": "Windows",
            "Sec-CH-UA-Mobile": "?0",
        }

        # Merge spoofed headers with existing request headers
        headers = request.headers
        headers.update(spoofed_headers)

        # Continue the request with modified headers
        route.continue_(headers=headers)

    def randomize_browser_context(self):
        pass

        # self.context.set_permissions(["geolocation", "notifications"])
        # self.page.set_viewport_size(self.resolution)
        #
        # self.context = self.browser.new_context(
        #     locale=proxy_details["locale"],
        #     timezone_id=proxy_details["timezone"],
        #     user_agent=get_random_user_agent(),
        #     storage_state=self.account.get_session(),
        #     bypass_csp=True
        # )

    def go_to_instagram(self):
        self.account.add_cli('Going to Instagram page ...')
        self.pause(4000, 5000)
        retries = 3
        for attempt in range(retries):
            try:
                self.page.goto('https://www.instagram.com/', timeout=200000)
                break
            except Exception as e:
                self.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                self.pause(2000, 3000)

        self.account.add_cli('After Instagram loaded and before timeout')
        self.pause(4000, 6000)

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

        try:
            self.account.add_cli('Closing MLX profile ...')
            Requests().close_mlx_profile(self.profile_id)
        except Exception as e:
            self.account.add_cli(f'Problem Closing Profile : {str(e)}')

    def goto(self, url, timeout=30000):
        try:
            self.page.goto(url, timeout=timeout)
            self.pause(2000, 3000)
            went_wrong = self.something_went_wrong()
            automated_behaviour = self.suspect_automate_behavior_handler()

            if went_wrong or automated_behaviour:
                self.page.goto(url, timeout=timeout)

            self.turn_on_notif()

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

            try:
                self.pause(2000, 3000)
                self.page.get_by_role("button", name="Reload page").click()

            except Exception as e:
                self.account.add_cli(str(e))
                pass
            return True

        return False

    def unusual_login_detected(self):
        if self.is_visible_by_text('We Detected An Unusual Login') or self.is_visible_by_text(
                "We've detected an unusual login attempt"):
            self.account.add_cli('Unusual Login Detected')
            self.page.get_by_role("button", name="This Was Me").click()
            return True

        return False

    def we_removed_some_content_or_messages_handler(self):
        if self.is_visible_by_text('What happened') or self.is_visible_by_text(
                "We removed some content or messages"):
            self.account.add_cli('We removed some content or messages')

            try:
                self.page.locator('div.wbloks_1[role="button"]').first.click()
                self.pause(4000, 5000)

                self.goto('https://www.instagram.com/')
                self.pause(3000, 4000)
            except Exception as e:
                pass

    def your_post_goes_against_our_community_handler(self):
        if self.is_visible_by_text('Your Post Goes Against Our Community') or self.is_visible_by_text(
                "We removed your post because it goes against our"):
            self.account.add_cli('Your Post Goes Against Our Community')

            try:
                self.page.get_by_role("button", name="OK").first.click()
            except Exception as e:
                self.page.locator(
                    'div.x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x972fbf.xcfux6l.x1qhh985.xm0m39n.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu').first.click()

            self.pause(3000, 4000)

    def not_connect_to_the_internet(self):
        if self.is_visible_by_text("We couldn't connect to Instagram"):
            raise NotConnectedToTheInternetError(
                "We couldn't connect to Instagram. Make sure you're connected to the internet and try again.")

    def password_is_incorrect_handler(self):
        if self.is_visible_by_text('your password was incorrect'):
            self.account.set_state(state='suspended', log='Your password was incorrect')
            raise YourPasswordWasIncorrectError('Your password was incorrect')

    def problem_logging_in_handler(self):
        if self.is_visible_by_text('was a problem logging you into Instagram'):
            raise ProblemLogingYouError('There was a problem logging you into Instagram .please try again soon')

    def suspended_account_handler(self):
        if self.is_visible_by_text('We suspended your account'):
            self.page.get_by_role("button", name="Appeal", exact=True).click(timeout=3000)
            self.pause(5000, 6000)

            raise AccountSuspendedError('We suspended your account')

    def disabled_account_handler(self):
        if self.is_visible_by_text('Your account has been disabled') or self.is_visible_by_text(
                'We disabled your account'):
            raise AccountDisabledError('We disabled your account')

    def appeal_submitted_handler(self):
        if self.is_visible_by_text('You submitted an appeal') or self.is_visible_by_text(
                'It usually takes us just over a day to review your information'):
            raise AppealSubmittedError('Appeal submitted')

    def upload_your_id_handler(self):
        if self.is_visible_by_text('Upload your ID') or self.is_visible_by_text(
                'We need a photo of your official ID'):
            raise UploadYourIdError('Upload your ID')

    def suspect_automate_behavior_handler(self):

        if self.is_visible_by_text('suspect automated behavior') or self.is_visible_by_text(
                'suspect automated behaviour') or self.is_visible_by_text(
            'To prevent your account from being temporarily restricted or permanently disabled'):

            try:
                self.pause(3000, 4000)
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
            self.pause(2000, 3000)
            self.page.get_by_role("button", name="Turn On", exact=True).click(timeout=3500)
            self.pause(5000, 6000)
        except:
            self.account.add_cli("Turn On doesn't exists")
            pass

    def find_friends_and_accounts_like_you(self):

        self.account.add_cli('Find friends and accounts you like ...')
        if self.is_visible_by_text('Find friends and accounts you like'):

            try:
                self.pause(2000, 3000)
                self.page.get_by_role("button", name="Next", exact=True).first.click(timeout=3500)
            except:
                pass

    def save_session(self):

        storage_state = self.page.context.storage_state()
        storage_state_json = json.dumps(storage_state)
        self.account.save_session(storage_state_json)
