from .BasePlaywright import BasePlaywright
import traceback
from .InstagramButtonHandlerMixin import InstagramButtonHandlerMixin
from .InstagramSuspensionHandlerMixin import InstagramSuspensionHandlerMixin


class Instagram(BasePlaywright, InstagramButtonHandlerMixin, InstagramSuspensionHandlerMixin):
    account = None

    def go_to_instagram(self):
        try:
            self.account.add_cli('Going to Instagram page ...')
            self.page.goto('https://www.instagram.com/', timeout=200000)
            self.account.add_cli('After instagram loaded and before timeout')
            self.pause(5000, 6000)
            self.account.add_cli('After 5000-6000 timeout')
            self.allow_cookies()
            self.account.add_cli('After allowing cookies')
            self.suspect_automate_behavior_handler()
            return self

        except:
            self.handle_exception('Problem opening Instagram page')

    def go_to_profile_page(self):
        self.account.add_cli('Going to Accounts profile page')
        self.page.goto('https://www.instagram.com/accounts/edit/')
        self.account.add_cli('Profile page should be loaded before timeout')
        self.pause(3000, 4000)
        self.account.add_cli('After profile load timeout')

    def go_to_app_setting_page(self):
        self.account.add_cli('Going to App setting page')
        self.page.goto('https://accountscenter.instagram.com/?entry_point=app_settings')
        self.account.add_cli('App setting page should be loaded before timeout')
        self.pause(3000, 4000)
        self.account.add_cli('After app setting load timeout')

        self.click_on_users_instagram()
        self.pause(3000, 4000)

    def change_name(self, name):

        self.click_on_profile_attribute("Name")

        if self.is_visible_by_text('You can only change your name twice'):
            self.page.get_by_role("button", name="Back").click()
            raise Exception('You can only change your name twice')

        self.pause(3000, 4000)
        self.fill_property("Name", name)
        self.page.get_by_role("button", name="Done").click(timeout=5000)
        self.pause(4000, 5000)

    def change_avatar(self, path):
        self.click_on_profile_attribute("Profile picture")
        self.pause(2000, 3000)

        self.account.add_cli('Setting input file')
        self.page.locator("input[accept='image/png,image/jpg,image/heif,image/heic']").nth(0).set_input_files(path)
        self.account.add_cli('After input file and before 15000 - 17000 timeout')
        self.pause(15000, 17000)
        self.account.add_cli('after time out and before save')
        self.click_by_role('Save')
        self.account.add_cli('after save and before 4000-5000 timeout')
        self.pause(4000, 5000)
        self.account.add_cli('After 4000-5000 timeout')
        self.page.get_by_role("button", name="Back").click()

    def change_username(self, username):
        self.go_to_profile_page()

        self.click_on_profile_attribute("Username")
        self.pause(3000, 4000)

        self.fill_property("Username", username)
        self.pause(4000, 5000)

        if self.is_visible_by_text('Username is not available'):
            raise Exception('Username is not available')

        self.click_and_raise_if_cant(
            'Clicking on Done button',
            "Done",
            "Problem clicking on done button",
            "button"
        )

    def change_bio(self, bio):
        self.page.get_by_placeholder("Bio").fill(bio)
        self.pause(2000, 3000)
        self.page.get_by_role("button", name="Submit").click()
        self.pause(3000, 4000)

    def follow(self, lead):
        try:
            self.page.goto(f'https://www.instagram.com/{lead.username}', timeout=50000)
            self.pause(5000, 5500)
            self.page.get_by_role("button", name="Follow", exact=True).click()
            self.pause(3000, 4000)
        except Exception as e:
            self.handle_exception(f'Problem changing bio : {str(e)}', 'None')

    def send_dm(self, lead):
        self.page.goto(f'https://www.instagram.com/{lead.username}')
        self.pause(6000, 6500)
        self.page.get_by_role("button", name="Message", exact=True).click()
        self.pause(4000, 5000)
        self.page.get_by_role("textbox", name="Message").fill(lead.dm_text)
        self.pause(2000, 2500)
        self.page.get_by_role("textbox", name="Message").press("Enter")
        self.pause(4000, 5000)

    def is_not_logged_in(self):
        return self.is_visible_by_text('Phone number, username, or email') or self.is_visible_by_text(
            "Don't have an account")

    def fill_username_password(self):
        self.page.get_by_label("Phone number, username, or email").fill(self.account.username)
        self.pause(2000, 3000)
        self.page.get_by_label("Password").fill(self.account.password)
        self.pause(2000, 3000)
        self.page.get_by_role("button", name="Log in", exact=True).click()
        self.pause(8000, 9000)

        return self

    def need_2f_authentication(self):
        self.account.add_cli('')
        return self.is_visible_by_text('Enter the 6-digit code generated by') or self.is_visible_by_text(
            "If you're unable to receive a login code from an authentication app")

    def two_factor_authentication_process(self):
        page1 = self.context.new_page()
        self.account.add_cli('Going to bulkacc page to get the code')
        page1.goto("https://bulkacc.com/twofactorenable")
        self.account.add_cli('Bulk acc should be loaded and before 200-300 timeout')
        self.pause(2000, 3000)
        self.account.add_cli('After 2000-3000 timeout')
        page1.get_by_placeholder("Input your 2FA secret key").fill(self.account.secret_key)
        self.pause(1000, 2000)
        page1.get_by_role("button", name="Get code").click()
        self.pause(2000, 3000)

        code = page1.locator('#twoFactorCode').text_content()
        self.account.add_cli(f'Code is {code}')

        page1.close()
        self.pause(1000, 2000)

        self.page.get_by_label("Security Code").fill(code)
        self.page.get_by_role("button", name="Confirm").click()
        self.account.add_cli('confirm clicked, before 5000-6000 timeout')

        self.pause(5000, 6000)
        self.account.add_cli('After 5000-6000 timeout')

        if self.is_visible_by_text('We Detected An Unusual Login'):
            print('unusual login attempt')
            self.page.get_by_role("button", name="This Was Me").click()
            self.pause(4000, 5000)

    def log_in(self):
        self.go_to_instagram()
        self.pause(2000, 3000)

        try:
            self.continue_as()
            self.enter_your_mobile_number_handler()

            if self.is_not_logged_in():
                self.account.add_cli('User is not logged in before trying to login ...')
                self.fill_username_password()
                self.account.add_cli('after user login ...')
                self.allow_cookies()
                self.password_is_incorrect_handler()
                self.problem_logging_in_handler()

            if self.need_2f_authentication():
                self.two_factor_authentication_process()

            self.unusual_login_attempt_handler()
            self.suspended_account_handler()
            self.suspect_automate_behavior_handler()
            self.help_us_confirm_its_you_handler()
            self.save_info()
            self.turn_on_notif()
            self.save_session()

        except Exception as e:
            self.handle_exception(str(e))

        return self

    def set_name(self):
        pass

    def set_profile_info(self):
        pass

    def handle_exception(self, reason, _type='raise'):
        self.account.add_cli(reason)
        self.account.add_log(traceback.format_exc())

        if _type == 'raise':
            raise Exception(reason)

    def save_session(self):
        self.account.save_session(self.page.context.storage_state())
