from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import random
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Template import get_a, delete


class BrowserChangeUsernameEvent(InstagramMiddleware):
    base = None
    username = None
    username_counter = 0
    command = 0

    def execute(self):
        if self.ig.account.username_changed:
            return self.ig.account.add_cli(f"Account's username has been changed already.")

        self.get_username()

        if not self.username:
            return self.ig.account.add_cli(f"We don't have a username for : {self.ig.account.username}")

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem changing Username : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.base = BrowserBaseEvent(self.ig)
        self.ig.account.set_state('set username', 'app_state')
        self.command = self.ig.account.create_command('set username', 'processing')

    def change_hook(self):

        self.base.go_to_profile_page()
        self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click()
        self.ig.page.locator(f"text=Username").click()
        self.ig.pause(3000, 4000)

        self.fill_username()
        self.ig.pause(4000, 5000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('username', self.username)
        self.ig.account.set('username_changed', 1)

    def get_username(self):
        self.username = get_a('username', self.ig.account).text

        # we delete this username from database to don't use for another account
        delete('username', self.username)
        self.ig.account.add_cli(f'Selected username: {self.username}')

    def fill_username(self):
        self.ig.page.get_by_label("Username").fill(self.username)
        self.ig.pause(3000, 4000)

        while self.ig.is_visible_by_text('Username is not available'):
            self.ig.account.add_cli(f'Selected username is not available')
            self.get_username()
            self.fill_username()
            self.username_counter += 1

            if self.username_counter >= 3:
                raise Exception('3 Times username exists exceeded')

        self.ig.page.get_by_role("button", name="Done").click(timeout=5000)
        self.ig.pause(4000, 5000)
