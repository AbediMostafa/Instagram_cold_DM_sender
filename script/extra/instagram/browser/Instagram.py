from script.extra.events.browser_events.BasePlaywright import BasePlaywright
import traceback
from script.extra.instagram.browser.InstagramButtonHandlerMixin import InstagramButtonHandlerMixin
from script.extra.instagram.browser.InstagramSuspensionHandlerMixin import InstagramSuspensionHandlerMixin


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







    def log_in(self):
        self.go_to_instagram()
        self.pause(2000, 3000)

        try:
            self.continue_as()
            self.enter_your_mobile_number_handler()

            if self.is_not_logged_in():
                self.account.add_cli('User is not logged in before trying to login ...')
                self.fill_username_password()

                for i in range(7):
                    self.account.add_cli('after user login ...')

                    if self.need_2f_authentication():
                        self.two_factor_authentication_process()

                    self.allow_cookies()
                    self.password_is_incorrect_handler()
                    self.problem_logging_in_handler()
                    self.page.wait_for_timeout(1000)

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
