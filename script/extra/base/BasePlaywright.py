from script.extra.base.BrowserHandlerFactory import BrowserHandlerFactory
from script.extra.exceptions import *
import json
import random
from script.extra.base.AdsPowerHandler import AdsPowerHandler


class BasePlaywright:
    browser = None
    context = None
    page = None
    proxy = None

    def __init__(self, account):
        self.account = account
        self.handler = AdsPowerHandler(account)

    def init(self):
        self.handler.create_profile()
        self.handler.start_browser()

        self.browser = self.handler.get_browser()
        self.context = self.handler.get_context()
        self.page = self.handler.get_page()

        # Transfer proxy reference from handler for use in API requests
        self.proxy = self.handler.proxy

        return self

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
        self.handler.cleanup()
        self.handler.delete_adspower_cache()
        self.handler.delete_profile()

    def pause(self, min_ms, max_ms):
        self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    def allow_cookies(self):
        self.account.add_cli(f'Trying to allow cookies ...')

        for i in range(7):
            try:
                try:
                    self.page.locator('button', has_text='Allow All Cookies').click(timeout=1500)
                except:

                    try:
                        self.page.locator('button', has_text='Allow all cookies').click(timeout=1500)
                    except:
                        self.page.locator('div[role="button"]', has_text='Allow all cookies').click(timeout=1500)

                self.account.add_cli(f'Clicked on allow cookies')
                return True
            except Exception as e:
                pass

    # def is_visible_by_text(self, text: str, exact: bool = False, timeout: int = 5000) -> bool:
    def is_visible_by_text(self, text, timeout: int = 5000):
        import re

        try:
            regex = re.compile(re.escape(text), re.I)
            locator = self.page.get_by_text(regex)
            count = locator.count()

            for i in range(count):
                if locator.nth(i).is_visible():
                    print(f"Element {i} for '{text}' is visible")
                    return True

            return False
        except Exception as e:
            print(f"Error checking '{text}': {e}")
            return False

    def is_visible_by_texts(self, texts, timeout: int = 5000):
        return any(self.is_visible_by_text(text, timeout) for text in texts)

    def two_factor_authentication_process(self):

        self.page.get_by_label("Security Code").press_sequentially(self.account.get_verification_code(), delay=100)

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
                self.page.locator('div.wbloks_1[role="button"]').first.click(timeout=3500)
                self.pause(4000, 5000)

                self.go_to_instagram()
                self.pause(3000, 4000)
            except Exception as e:
                pass

    def review_and_agree_handler(self):
        if self.is_visible_by_text('Review and Agree') or self.is_visible_by_text(
                "Changes to How We Manage Data"):
            self.account.add_cli('Review and Agree, Changes to How We Manage Data')

            try:
                self.page.get_by_role("button", name="Next", exact=True).click(timeout=3500)
                self.pause(4000, 5000)

                self.page.get_by_role("button", name="Agree to Terms", exact=True).click(timeout=3500)
                self.pause(4000, 5000)

                self.go_to_instagram()
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

    def check_your_text_messages(self):
        if self.is_visible_by_text('Check your text messages'):
            raise CheckYourTextMessages('Check your text messages')

    def choose_a_way_to_confirm(self):
        if self.is_visible_by_text('Choose a way to confirm'):
            raise CheckYourTextMessages('Choose a way to confirm')

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
        self.account.add_cli('Save session ...')

        storage_state = self.page.context.storage_state()
        storage_state_json = json.dumps(storage_state)
        self.account.save_session(storage_state_json)
