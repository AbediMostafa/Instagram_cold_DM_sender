from script.extra.playwright.base_actions.BaseAction import BaseAction
from script.extra.exceptions import *
from script.extra.helper import go_to_page
from script.extra.modules.adspower.Adspower import Adspower


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

        if self.ig.is_visible_by_text('suspect automated behavior') or self.ig.is_visible_by_text(
                'suspect automated behaviour') or self.ig.is_visible_by_text(
            'To prevent your account from being temporarily restricted or permanently disabled'):

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

        if self.ig.is_visible_by_text('Choose if we process your data') or self.ig.is_visible_by_text(
                'you can choose whether you consent to us processing'):

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

        if self.ig.is_visible_by_text('Changes to How We Manage Data') or self.ig.is_visible_by_text(
                'Review and Agree'):
            self.ig.pause(1000, 2000)
            self.ig.account.add_cli('Changes to How We Manage Data ...')
            self.ig.page.get_by_role("button", name='Next').click(timeout=5000)
            self.ig.pause(5000, 6000)
            self.ig.page.get_by_role("button", name='Agree to Terms').click(timeout=3000)
            self.ig.pause(3500, 5500)

    def continue_as_handler(self):
        if self.ig.is_visible_by_text('Continue as') or self.ig.is_visible_by_text(
                'Continue As') or self.ig.is_visible_by_text('continue As'):
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
        if self.ig.is_visible_by_text('your password was incorrect'):
            raise YourPasswordWasIncorrectError('Your password was incorrect')

    def problem_logging_in_handler(self):
        if self.ig.is_visible_by_text('was a problem logging you into Instagram'):
            raise ProblemLogingYouError('There was a problem logging you into Instagram .please try again soon')

    def login_info_is_incorrect(self):
        # The login information you entered is incorrect
        if self.ig.is_visible_by_text('login information you entered is incorrect'):
            raise ProblemLogingYouError('login information you entered is incorrect')

    def page_could_not_be_loaded_handler(self):
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            self.ig.account.add_cli("There's an issue and the page could not be loaded")

            self.ig.pause(2000, 3000)
            go_to_page(self.ig, 'https://www.instagram.com/', "Home")
            self.ig.pause(2000, 3000)

    def fill_code_sent_to_email(self):
        if self.ig.is_visible_by_text('Enter the code we sent to') or self.ig.is_visible_by_text('Check your email'):
            raise FillCodeSentToError('Enter the code we sent to your email')

    def enter_your_mobile_number(self):
        if self.ig.is_visible_by_text('Enter your mobile number'):
            raise EnterYourMobileError('Enter your mobile number')

    def we_sent_a_code_to_whatsapp(self):
        # Check your WhatsApp messages
        # Enter the code we sent to your WhatsApp account
        if self.ig.is_visible_by_text('We sent a code to WhatsApp') or self.ig.is_visible_by_text(
                'Check your WhatsApp messages') or self.ig.is_visible_by_text(
            'Enter the code we sent to your WhatsApp account'):
            raise EnterYourMobileError('We sent a code to WhatsApp')

    def suspended_account_handler(self):
        if self.ig.is_visible_by_text('We suspended your account'):
            self.ig.page.get_by_role("button", name="Appeal", exact=True).click(timeout=3000)
            self.ig.pause(5000, 6000)

            raise AccountSuspendedError('We suspended your account')

    def disabled_account_handler(self):
        if self.ig.is_visible_by_text('Your account has been disabled') or self.ig.is_visible_by_text(
                'We disabled your account'):
            raise AccountDisabledError('We disabled your account')

    def appeal_submitted_handler(self):
        if self.ig.is_visible_by_text('You submitted an appeal') or self.ig.is_visible_by_text(
                'It usually takes us just over a day to review your information'):
            raise AppealSubmittedError('Appeal submitted')

    def check_your_text_messages(self):
        if self.ig.is_visible_by_text('Check your text messages'):
            raise CheckYourTextMessages('Check your text messages')

    def choose_a_way_to_confirm(self):
        if self.ig.is_visible_by_text('Choose a way to confirm'):
            raise CheckYourTextMessages('Choose a way to confirm')

    def upload_your_id_handler(self):

        if self.ig.is_visible_by_text('Upload your ID') or self.ig.is_visible_by_text(
                'We need a photo of your official ID'):
            raise UploadYourIdError('Upload your ID')

    def enter_your_email_handler(self):
        if self.ig.is_visible_by_text('Enter your email') or self.ig.is_visible_by_text(
                "We’ll send a confirmation code to this email"):
            raise EnterYourEmailError('Enter your email address')

    def enter_confirmation_code_handler(self):
        if self.ig.is_visible_by_text('Enter confirmation code'):
            raise EnterYourEmailError('Enter confirmation code')

    # Confirm you're human to use your account,

    def confirm_you_are_human_to_use_your_account(self):
        if self.ig.is_visible_by_text("Confirm you're human"):

            try:
                self.ig.page.get_by_role("button", name="Continue").click(timeout=3000)
            except:
                raise HelpUsConfirmItsYouError("Confirm you're human")

    def add_a_phone_number(self):
        if self.ig.is_visible_by_text('Add a phone number to get back into Instagram') or self.ig.is_visible_by_text(
                "We will send a confirmation code via SMS to your phone"):
            raise AddAPhoneNumberError('Add a phone number to get back into Instagram')

    def confirm_you_own_this_account(self):
        # Help us confirm you own this account
        if self.ig.is_visible_by_text('confirm that you own this account') or self.ig.is_visible_by_text(
                "You'll need to verify your identity") or self.ig.is_visible_by_text(
            "Help us confirm you own this account"):
            raise ConfirmYouOwnThisAccount('Help us confirm that you own this account')

    def we_are_working_on_getting_this_fixed(self):
        if self.ig.is_visible_by_text('Sorry, something went wrong') or self.ig.is_visible_by_text(
                "working on getting this fixed as soon as we can"):
            raise SomethingWentWrong('Sorry, something went wrong')

    def help_us_confirm_its_you_handler(self):
        if self.ig.is_visible_by_text('Help us confirm it') or self.ig.is_visible_by_text(
                "Help us confirm that it's you"):
            raise HelpUsConfirmItsYouError("Help us confirm it's you")

    def feedback_required(self):
        if self.ig.is_visible_by_text('feedback_required') or self.ig.is_visible_by_text("feedback required"):
            self.ig.account("Setting this account's is_used to 0 ...")
            self.ig.account.set('is_used', 0)

            # raise FeedbackRequired("feedback required")

    def change_password_handler(self):

        if self.ig.is_visible_by_text('Change your password to secure your account') or self.ig.is_visible_by_text(
                'Someone may have your password') or self.ig.is_visible_by_text(
            'Change Your Password to Secure Your Account'):
            raise ChangePasswordError('Change Your Password to Secure Your Account')

    def check_the_security_code(self):
        if self.ig.is_visible_by_text('check the security code'):
            raise CheckTheSecurityCode('Please check the security code.')
