from script.extra.playwright.base_actions.BaseAction import BaseAction
from script.extra.exceptions import *
from script.extra.helper import go_to_page
from script.extra.modules.adspower.Adspower import Adspower
import re


class ErrorIndicators(BaseAction):

    def page_is_not_visible_handler(self):
        if self.ig.is_visible_by_text("this page isn't available") or self.ig.is_visible_by_text(
                "The link you followed may be broken, or the page may have been removed"):
            raise Exception("Sorry, this page isn't available")

    def something_went_wrong_handler(self):
        for _ in range(7):
            if self.ig.is_visible_by_text("Something went wrong"):
                raise Exception("Something went wrong")

            self.ig.pause(1000, 1100)

    def not_every_one_can_message_this_account_handler(self, lead):
        if self.ig.is_visible_by_text("Not everyone can message this account"):
            lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)
            raise Exception("Not everyone can message this account")

    def send_more_messages_after_invite_accepted(self):
        if self.ig.is_visible_by_text(
                "You can send more messages after your invite is accepted") or self.ig.is_visible_by_text(
            "You can send more messages after they accept"):
            raise Exception("You can send more messages after your invite is accepted")

    def suspect_automate_behavior_handler(self):
        messages = ['suspect automated behavior',
                    'suspect automated behaviour',
                    'To prevent your account from being temporarily restricted',
                    ]

        if self.ig.is_visible_by_texts(messages):

            try:
                self.ig.pause(1000, 2000)
                self.ig.account.add_cli('We suspect automated behavior on your account')
                self.ig.page.get_by_role("button", name='Dismiss').click(timeout=5000)
                self.ig.pause(5000, 6000)

            except Exception as e:
                raise Exception(f'Problem clicking on Dismiss:{str(e)}')

    def use_another_profile(self):
        import re

        if self.ig.is_visible_by_text('Use another profile'):

            try:
                self.ig.pause(1000, 2000)
                self.ig.account.add_cli('Use another profile')
                # self.ig.page.get_by_role("button", name='Use another profile').click(timeout=5000)
                self.ig.page.get_by_role("button", name=re.compile(r"Use another profile", re.I)).click(timeout=3000)

                self.ig.pause(5000, 6000)

            except Exception as e:
                raise Exception(f'Problem clicking on use_another_profile:{str(e)}')

    #     Use another profile

    def choose_if_we_process_your_data(self):
        # Choose if we process your data for ads
        messages = [
            'Choose if we process your data',
            'you can choose whether you consent to us processing',
        ]

        if self.ig.is_visible_by_texts(messages):

            try:
                self.ig.pause(1000, 2000)
                self.ig.account.add_cli('Choose if we process your data for ads ...')
                self.ig.page.get_by_role("button", name='Get started').click(timeout=5000)
                self.ig.pause(5000, 6000)

            except Exception as e:
                raise Exception(f'Problem clicking on Dismiss:{str(e)}')

            self.ig.pause(5000, 6000)

            try:
                self.ig.page.locator("role=radio[name='Use free of charge with ads']").click(timeout=5000)

            except Exception as e:
                self.ig.account.add_cli("Problem clicking on radio[name='Use free of charge with ads']")
                self.ig.page.click("input[name='afs_choice_input_key'][value='PA']")

            self.ig.pause(2000, 2500)

            self.ig.page.get_by_role("button", name='Continue').click(timeout=3000)
            self.ig.pause(3500, 5500)
            self.ig.page.get_by_role("button", name='Agree').click(timeout=3000)
            self.ig.pause(3500, 4500)
            self.ig.page.get_by_role("button", name='Not interested').click(timeout=3000)
            self.ig.pause(3500, 4500)

    def changes_to_how_we_manage_data(self):
        # Changes to How We Manage Data

        messages = [
            'Changes to How We Manage Data',
            'Review and Agree'
        ]

        if self.ig.is_visible_by_texts(messages):
            self.ig.pause(1000, 2000)
            self.ig.account.add_cli('Changes to How We Manage Data ...')
            self.ig.page.get_by_role("button", name='Next').click(timeout=5000)
            self.ig.pause(5000, 6000)
            self.ig.page.get_by_role("button", name='Agree to Terms').click(timeout=3000)
            self.ig.pause(3500, 5500)

    def continue_as_handler(self):
        if self.ig.is_visible_by_text('Continue as'):

            self.ig.account.add_cli('Continue as is visible, Clicking on it')
            try:
                self.ig.page.locator('//button[span[contains(text(), "Continue as")]]').click(timeout=3000)
            except:
                try:
                    self.ig.page.locator('.//span[contains(text(), "Continue as")]]').click(timeout=3000)
                except Exception as e:
                    self.ig.page.locator("span:has-text('Continue as')").click(timeout=4000)

            self.ig.page.wait_for_timeout(4000)

    def choose_if_we_process_your_data_for_ads(self):
        if self.ig.is_visible_by_text('if we process your data for ads'):

            try:
                self.ig.page.get_by_role("button", name='Not now').click(timeout=5000)
            except:
                try:
                    self.ig.page.locator(
                        'div.x1i10hfl.xjqpnuy.xc5r6h4.xqeqjp1.x1phubyo.x972fbf.x10w94by.x1qhh985.x14e42zd.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x14z9mp.xat24cr.x1lziwak.x2lwn1j.xeuugli.xexx8yu.x18d9i69.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x1lku1pv.x1a2a7pz.x6s0dn4.xjyslct.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x9f619.x1ypdohk.x78zum5.x1f6kntn.xwhw2v2.xl56j7k.x17ydfre.x1n2onr6.x2b8uid.xlyipyv.x87ps6o.x14atkfc.x5c86q.x18br7mf.x1i0vuye.x6nl9eh.x1a5l9x9.x7vuprf.x1mg3h75.x5kalc8.x106a9eq.x1xnnf8n.x1aavi5t.x1h6iz8e.xixcex4.xk4oym4.xl3ioum').click(
                        timeout=3000)
                except Exception as e:
                    self.ig.page.locator("div:has-text('Not now')").click(timeout=4000)

    def not_connect_to_the_internet(self):
        if self.ig.is_visible_by_text("We couldn't connect to Instagram"):
            raise NotConnectedToTheInternetError(
                "We couldn't connect to Instagram. Make sure you're connected to the internet and try again.")

    def password_is_incorrect_handler(self):
        # The password you entered is incorrect.
        if self.ig.is_visible_by_text('your password was incorrect'):
            raise YourPasswordWasIncorrectError('Your password was incorrect')

    def problem_logging_in_handler(self):
        if self.ig.is_visible_by_text('was a problem logging you into Instagram'):
            raise ProblemLogingYouError('There was a problem logging you into Instagram .please try again soon')

    def login_info_is_incorrect(self):
        # The login information you entered is incorrect
        if self.ig.is_visible_by_text('login information you entered is incorrect'):
            raise ProblemLogingYouError('login information you entered is incorrect')

    def choose_a_way_to_recover(self):
        # The login information you entered is incorrect
        if self.ig.is_visible_by_text('Choose a way to recover'):
            raise ProblemLogingYouError('Choose a way to recover')

    def page_could_not_be_loaded_handler(self):
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            self.ig.account.add_cli("There's an issue and the page could not be loaded")

            self.ig.pause(2000, 3000)
            go_to_page(self.ig, 'https://www.instagram.com/', "Home")
            self.ig.pause(2000, 3000)

    def fill_code_sent_to_email(self):
        messages = [
            'Enter the code we sent to',
            'Check your email',
            "Enter the 6-digit code we sent to the email"
        ]
        if self.ig.is_visible_by_texts(messages):
            raise FillCodeSentToError('Enter the code we sent to your email')

    def enter_your_mobile_number(self):
        if self.ig.is_visible_by_text('Enter your mobile number'):
            raise EnterYourMobileError('Enter your mobile number')

    def we_sent_a_code_to_whatsapp(self):
        # Check your WhatsApp messages
        messages = [
            'We sent a code to WhatsApp',
            'Check your WhatsApp messages',
            'Enter the code we sent to your WhatsApp'
        ]
        if self.ig.is_visible_by_texts(messages):
            raise EnterYourMobileError('We sent a code to WhatsApp')

    def suspended_account_handler(self):
        if self.ig.is_visible_by_text('We suspended your account'):

            try:
                self.ig.page.get_by_role("button", name="Appeal", exact=True).click(timeout=3000)
                self.ig.pause(5000, 6000)
            except:
                pass

            raise AccountSuspendedError('We suspended your account')

    def disabled_account_handler(self):
        messages = [
            'Your account has been disabled',
            'We disabled your account'
        ]

        if self.ig.is_visible_by_texts(messages):
            raise AccountDisabledError('We disabled your account')

    def appeal_submitted_handler(self):
        messages = [
            'You submitted an appeal',
            'It usually takes us just over a day to review your information'
        ]

        if self.ig.is_visible_by_texts(messages):
            raise AppealSubmittedError('Appeal submitted')

    def check_your_text_messages(self):
        if self.ig.is_visible_by_text('Check your text messages'):
            raise CheckYourTextMessages('Check your text messages')

    def choose_a_way_to_confirm(self):
        if self.ig.is_visible_by_text('Choose a way to confirm'):
            raise CheckYourTextMessages('Choose a way to confirm')

    def upload_your_id_handler(self):
        messages = [
            'Upload your ID',
            'We need a photo of your official ID'
        ]

        if self.ig.is_visible_by_texts(messages):
            raise UploadYourIdError('Upload your ID')

    def enter_your_email_handler(self):
        messages = [
            'Enter your email',
            "We’ll send a confirmation code to this email",
        ]
        if self.ig.is_visible_by_texts(messages):
            raise EnterYourEmailError('Enter your email address')

    def enter_confirmation_code_handler(self):
        if self.ig.is_visible_by_text('Enter confirmation code'):
            raise EnterYourEmailError('Enter confirmation code')

    # Confirm you're human to use your account,

    def confirm_you_are_human_to_use_your_account(self):
        if self.ig.is_visible_by_text("Confirm you're human"):
            try:
                self.ig.page.get_by_role("button", name="Continue").click(timeout=3000)
                self.ig.pause(1800, 3000)
                raise HelpUsConfirmItsYouError("Confirm you're human")
            except:

                raise HelpUsConfirmItsYouError("Confirm you're human")

    def add_a_phone_number(self):
        messages = [
            'Add a phone number to get back into Instagram',
            "We will send a confirmation code via SMS to your phone"
        ]
        if self.ig.is_visible_by_texts(messages):
            raise AddAPhoneNumberError('Add a phone number to get back into Instagram')

    def confirm_you_own_this_account(self):
        # Help us confirm you own this account
        messages = [
            'confirm that you own this account',
            "You'll need to verify your identity",
            "Help us confirm you own this account"
        ]

        if self.ig.is_visible_by_texts(messages):
            raise ConfirmYouOwnThisAccount('Help us confirm that you own this account')

    def we_are_working_on_getting_this_fixed(self):
        messages = [
            'Sorry, something went wrong',
            "working on getting this fixed as soon as we can",
        ]
        if self.ig.is_visible_by_texts(messages):
            raise SomethingWentWrong('Sorry, something went wrong')

    def help_us_confirm_its_you_handler(self):
        messages = [
            'Help us confirm it',
            "Help us confirm that it's you"
        ]
        if self.ig.is_visible_by_texts(messages):
            raise HelpUsConfirmItsYouError("Help us confirm it's you")

    def feedback_required(self):
        messages = [
            'feedback_required',
            "feedback required"
        ]
        if self.ig.is_visible_by_texts(messages):
            self.ig.account("Setting this account's is_used to 0 ...")
            self.ig.account.set('is_used', 0)

            # raise FeedbackRequired("feedback required")

    def change_password_handler(self):
        from script.extra.helper import generate_random_word
        messages = [
            'Change your password to secure your account',
            'Someone may have your password',
            'Change Your Password to Secure Your Account'
        ]

        if self.ig.is_visible_by_texts(messages):

            self.ig.account.add_cli("Change password page appeared")

            try:
                repeat_password_input = self.ig.page.get_by_label("New password confirmation")
                password = generate_random_word()

                self.ig.page.get_by_label("New password", exact=True).press_sequentially(password, delay=100,
                                                                                         timeout=3000)
                self.ig.pause(1800, 3000)

                try:
                    self.ig.page.get_by_label("New password confirmation").press_sequentially(password, delay=100,
                                                                                              timeout=3000)
                except:
                    self.ig.page.get_by_label("Confirm new password").press_sequentially(password, delay=100,
                                                                                         timeout=3000)

                self.ig.pause(2000, 3000)
                self.ig.page.get_by_role("button", name="Next", exact=True).click()
                self.ig.account.set('password', password)
                self.ig.account.add_cli("Password changed successfully")
                self.ig.pause(6000, 8000)

            except Exception as e:
                raise ChangePasswordError(str(e))

        if self.ig.is_visible_by_text('Your account was compromised') or self.ig.is_visible_by_text(
                'you shared your password with a service'):
            self.ig.account.add_cli("Your account was compromised ...")

            self.ig.page.get_by_role("button", name="Change Password", exact=True).click()
            self.ig.pause(1800, 3000)

            try:
                old_password = self.ig.page.get_by_label("Old password")
                self.ig.account.add_cli(f"Old password : {self.ig.account.password}")

                password = self.ig.account.password + '1'

                # password = generate_random_word()
                old_password.press_sequentially(self.ig.account.password, delay=100, timeout=3000)
                self.ig.pause(1800, 3000)

                self.ig.page.fill('input[name="new_password1"]', password)
                self.ig.pause(1800, 3000)
                self.ig.page.fill('input[name="new_password2"]', password)

                self.ig.pause(2000, 3000)
                self.ig.page.get_by_role("button", name="Change Password", exact=True).click()
                self.ig.pause(6000, 8000)

                if self.ig.is_visible_by_text(
                        'Your old password was entered incorrectly') or self.ig.is_visible_by_text(
                    'Please enter it again'):
                    raise ChangePasswordError('Your old password was entered incorrectly')

                self.ig.account.set('password', password)
                self.ig.account.add_cli("Password changed successfully")

            except Exception as e:
                raise ChangePasswordError(str(e))

    def check_the_security_code(self):
        if self.ig.is_visible_by_text('check the security code'):
            raise CheckTheSecurityCode('Please check the security code.')

    def trust_this_device(self):

        messages = [
            'trust this device to skip the step',
        ]
        if self.ig.is_visible_by_texts(messages):
            self.ig.page.get_by_role('button', name=re.compile(r'Trust this device', re.IGNORECASE)).click(timeout=4000)
            self.ig.account.add_cli('Trust this device clicked')
            self.ig.pause(4000, 5000)
