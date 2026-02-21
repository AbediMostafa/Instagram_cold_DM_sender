from script.extra.playwright.base_actions.AllowCookiesAction import AllowCookiesAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.extra.adapters.SettingAdapter import SettingAdapter
from script.models.Command import performed_command_count
from script.extra.exceptions import SuccessfulLogin
from script.extra.exceptions import *
from script.extra.helper import go_to_page
import random
import json
import re


# Confirm you're human to use your account, ecom_maven_tiktok_ed


class BrowserLoginEvent:
    command = None
    errors = None

    def __init__(self, ig):
        self.ig = ig
        self.errors = ErrorIndicators(self.ig)

    def init(self):

        self.ig.account.add_cli('Starting Login ...')

        for _ in range(2):
            self.check_for_login()

            self.ig.account.add_cli(f'Login loop for the {_} time ...')
            AllowCookiesAction(self.ig).start()
            self.errors.suspect_automate_behavior_handler()
            self.errors.use_another_profile()
            self.errors.choose_if_we_process_your_data()
            self.errors.changes_to_how_we_manage_data()
            self.errors.continue_as_handler()
            self.errors.choose_if_we_process_your_data_for_ads()
            self.errors.confirm_you_are_human_to_use_your_account()
            self.errors.enter_your_mobile_number()
            self.errors.we_sent_a_code_to_whatsapp()
            self.errors.enter_confirmation_code_handler()
            self.login_handler()
            self.two_fa_process()
            self.errors.check_the_security_code()
            self.errors.not_connect_to_the_internet()
            self.errors.password_is_incorrect_handler()
            self.errors.problem_logging_in_handler()
            self.errors.login_info_is_incorrect()
            self.errors.choose_a_way_to_recover()
            self.errors.page_could_not_be_loaded_handler()
            self.errors.fill_code_sent_to_email()
            self.unusual_login_detected()
            self.we_removed_some_content_or_messages_handler()
            self.your_post_goes_against_our_community_handler()
            self.errors.disabled_account_handler()
            self.errors.suspended_account_handler()
            self.errors.appeal_submitted_handler()
            self.errors.check_your_text_messages()
            self.errors.choose_a_way_to_confirm()
            self.errors.upload_your_id_handler()
            self.errors.enter_your_email_handler()
            self.errors.add_a_phone_number()
            self.errors.confirm_you_own_this_account()
            self.errors.we_are_working_on_getting_this_fixed()
            self.errors.help_us_confirm_its_you_handler()
            self.errors.feedback_required()
            self.errors.change_password_handler()
            self.please_log_in_to_continue()
            self.save_info()
            self.turn_on_notif()
            self.save_session()

            self.ig.pause(1000, 1200)

    def check_for_login(self):
        max_retries = 4

        for attempt in range(max_retries):
            try:
                self.ig.page.goto("https://www.instagram.com", timeout=100000)
                self.ig.pause(2000, 3000)
                self.the_messaging_tab_has_a_new_look()

                if self.ig.is_visible_by_text('Notifications') or self.ig.is_visible_by_text('Explore'):
                    self.ig.account.add_cli("User logged in before")

                    # if self.ig.page.url.rstrip("/") == "https://www.instagram.com/direct/inbox":
                    self.ig.pause(3000, 4000)
                    self.we_need_you_to_agree_to_the_following_items()
                    self.turn_on_notif()
                    self.the_messaging_tab_has_a_new_look()
                    self.save_session()
                    self.find_friends_and_accounts_you_like()
                    # self.follow_suggested()
                    raise SuccessfulLogin("Logged in successfully")

                # We're not logged in and should login
                return True

            except SuccessfulLogin as e:
                raise SuccessfulLogin("Logged in successfully")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")

            # Optionally: short pause before retrying
            self.ig.pause(5000, 7000)

        self.ig.account.add_cli("Failed to reach Instagram direct inbox after 5 attempts.")
        raise Exception("Failed to reach Instagram direct inbox after 5 attempts.")

    def we_need_you_to_agree_to_the_following_items(self):
        is_visible = self.ig.is_visible_by_text('we need you to agree to the following') or self.ig.is_visible_by_text(
            'Here are some of the key ways we may use your data')

        if is_visible:
            self.ig.page.wait_for_selector('input[type="checkbox"][role="switch"]')

            toggles = self.ig.page.query_selector_all('input[type="checkbox"][role="switch"]')

            for i, toggle in enumerate(toggles, start=1):
                toggle.click()
                self.ig.pause(1000, 1500)
                print(f"Clicked toggle {i}")

            self.ig.pause(3000,4000)

            self.ig.page.get_by_role("button", name=re.compile(r"I agree", re.I)).click(timeout=3000)
            self.ig.pause(3000,4000)
            self.ig.page.get_by_role("button", name=re.compile(r"Close", re.I)).click(timeout=3000)


    def two_fa_process(self):
        is_visible = self.ig.is_visible_by_text('Enter the 6-digit code generated by') or self.ig.is_visible_by_text(
            "If you're unable to receive a login code from an authentication app") or self.ig.is_visible_by_text(
            'Enter a 6-digit login code generated by')
        # Enter a 6-digit login code generated by an authentication app.
        # Enter a 6-digit login code generated by an authentication app.

        self.ig.account.add_cli('Checking two factor .... ')

        if is_visible:
            self.ig.account.add_cli('Two factor is visible ... ')
            self.ig.page.get_by_label("Security Code").press_sequentially(self.ig.account.get_verification_code(),
                                                                          delay=100)

            self.ig.page.get_by_role("button", name="Confirm").click()
            self.ig.account.add_cli('2FA confirm clicked')
            self.ig.pause(19000, 21000)

    def login_handler(self):
        is_visible = self.ig.is_visible_by_text('Phone number, username, or email') or self.ig.is_visible_by_text(
            "Don't have an account") or self.ig.is_visible_by_text(
            "Mobile number, username or email")

        if is_visible:
            self.ig.account.add_cli('User is not logged in before trying to login ...')
            self.fill_username_password()
            self.ig.pause(5000, 6000)

    def fill_username_password(self):

        input1 = self.ig.page.get_by_label("Phone number, username, or email")
        input2 = self.ig.page.get_by_label("Phone number, username or email address")
        input3 = self.ig.page.get_by_label("Mobile number, username or email")

        try:
            input1.fill('')
            input1.press_sequentially(self.ig.account.username, delay=100, timeout=4000)
            self.ig.account.add_cli('First locator didnt found')
        except:
            try:
                input2.fill('')
                input2.press_sequentially(self.ig.account.username, delay=100, timeout=6000)
                self.ig.account.add_cli('Second locator didnt found')

            except:
                input3.fill('')

                try:
                    input3.press_sequentially(self.ig.account.username, delay=100, timeout=6000)
                except:
                    self.ig.account.add_cli('Third locator didnt found')

        self.ig.pause(1800, 3000)
        self.ig.page.get_by_label("Password").fill('')
        self.ig.page.get_by_label("Password").press_sequentially(self.ig.account.password, delay=100, timeout=6000)
        self.ig.pause(2000, 3000)
        self.ig.page.get_by_role("button", name="Log in", exact=True).click()
        self.ig.pause(15000, 16000)

    def unusual_login_detected(self):
        if self.ig.is_visible_by_text('We Detected An Unusual Login') or self.ig.is_visible_by_text(
                "We've detected an unusual login attempt"):
            self.ig.account.add_cli('Unusual Login Detected')

            if self.ig.is_visible_by_text("we'll send you a security code to verify your identity"):
                raise HelpUsConfirmItsYouError("we'll send you a security code")

            try:
                self.ig.page.get_by_role("button", name="This Was Me").click(timeout=3000)
            except:
                self.ig.page.get_by_role("button", name=re.compile(r"this was me", re.IGNORECASE)).click()

            self.ig.pause(5000, 6000)

    def we_removed_some_content_or_messages_handler(self):
        if self.ig.is_visible_by_text('What happened') or self.ig.is_visible_by_text(
                "We removed some content or messages"):
            self.ig.account.add_cli('We removed some content or messages')

            try:
                self.ig.page.locator('div.wbloks_1[role="button"]').first.click(timeout=3000)
                self.ig.pause(4000, 5000)

                go_to_page(self.ig, 'https://www.instagram.com/', "Home")

                self.ig.pause(3000, 4000)
            except Exception as e:
                self.ig.account.add_cli(str(e))

    def your_post_goes_against_our_community_handler(self):
        if self.ig.is_visible_by_text('Your Post Goes Against Our Community') or self.ig.is_visible_by_text(
                "We removed your post because it goes against our"):
            self.ig.account.add_cli('Your Post Goes Against Our Community')

            try:
                self.ig.page.get_by_role("button", name="OK").first.click()
            except Exception as e:
                self.ig.page.locator(
                    'div.x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x972fbf.xcfux6l.x1qhh985.xm0m39n.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu').first.click()

            self.ig.pause(5000, 6000)

    def please_log_in_to_continue(self):
        if self.ig.is_visible_by_text('Please log in to continue'):
            self.ig.page.get_by_role("button", name="Log in").click(timeout=3000)

    def save_info(self):

        if self.ig.is_visible_by_text('Save info'):
            try:
                self.ig.account.add_cli('Saving information ...')
                self.ig.page.get_by_role("button", name="Save info", exact=True).click(timeout=3500)
                self.ig.pause(5000, 6000)
            except:
                self.ig.account.add_cli("Save info doesn't exists")

    def turn_on_notif(self):

        if self.ig.is_visible_by_text('Turn On notif'):

            try:
                self.ig.page.get_by_role("button", name=re.compile(r"Turn On", re.IGNORECASE)).click()
                self.ig.pause(4000, 5000)
            except:
                self.ig.account.add_cli("Turn On doesn't exists")
                pass

    #         The messaging tab has a new look

    def the_messaging_tab_has_a_new_look(self):
        if self.ig.is_visible_by_text('The messaging tab has'):
            self.ig.page.get_by_role("button", name=re.compile(r"OK", re.IGNORECASE)).click()

    def find_friends_and_accounts_you_like(self):
        if self.ig.is_visible_by_text('Find friends and accounts you like'):
            self.ig.account.add_cli('Find friends and accounts you like')
            try:
                self.ig.page.get_by_role("button", name=re.compile(r"next", re.IGNORECASE)).click()
            except Exception as e:
                self.ig.account.add_cli(f'Problem clicking on Find friends  :  {str(e)}')
            self.ig.pause(7000, 9000)

    def save_session(self):
        self.ig.account.add_cli('Saving session ...')

        storage_state = self.ig.page.context.storage_state()
        storage_state_json = json.dumps(storage_state)
        self.ig.account.save_session(storage_state_json)

    def follow_suggested(self):
        passed_days = self.ig.account.get_passed_days_since_creation() if self.ig.account.passed_days_since_creation is None else self.ig.account.passed_days_since_creation

        if passed_days < 25 :
            return self.ig.account.add_cli('Account is under 25 ... ')

        allowed_follows = random.randint(15, SettingAdapter.max_follow())
        allowed_follows = min(allowed_follows, passed_days)

        command_count = performed_command_count(self.ig.account, ['follow'], 24)

        self.ig.account.add_cli(f"performed follow :{command_count}, and allowed : {allowed_follows}")

        if command_count > allowed_follows:
            self.ig.account.add_cli(f"We are not allowed to follow")
            return False

        if self.ig.is_visible_by_text('Suggested for you'):
            random_follow_number = random.randint(2, 4)
            follow_buttons = self.ig.page.query_selector_all('button:has-text("Follow")')

            if len(follow_buttons) < 1 or len(follow_buttons) < random_follow_number:
                self.ig.account.add_cli(f'small follow button : {len(follow_buttons)} ')
                return False

            selected_follow_button = random.sample(follow_buttons, random_follow_number)
            count = 0

            for button in selected_follow_button:
                count += 1
                self.ig.account.add_cli(f"Following suggested user for time : {count}")

                command = self.ig.account.create_command('follow', 'processing')
                try:
                    # Generate a random number between 1 and 5
                    button.click()
                    command.update_cmd('state', 'success')
                    self.ig.account.add_cli("Lead followed successfully")

                except Exception as e:
                    self.ig.account.add_cli(f"Failed to follow suggested : {str(e)}")
                    command.update_cmd('state', 'fail')
                # Optional: Wait a bit between clicks to mimic human behavior and avoid rate limits
                self.ig.pause(1000, 3500)  # Wait for 1 second0

        self.ig.pause(2000, 3500)
