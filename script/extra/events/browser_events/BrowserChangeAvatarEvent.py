from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.helper import *
import shutil


class BrowserChangeAvatarEvent(InstagramMiddleware):
    base = None
    command = 0
    template = 0
    tmp = 0
    image_path = 0

    def execute(self):

        if self.ig.account.get_passed_days_since_creation() < 3:
            return self.ig.account.add_cli(f"Account is not old enough to change avatar")

        if self.ig.account.avatar_changed:
            return self.ig.account.add_cli(f"{self.ig.account.username}'s avatar has been changed already")

        self.template = self.ig.account.get_a_free_template('avatar')

        if not self.template:
            self.ig.account.add_cli(f"We don't have an avatar for : {self.ig.account.username}")

        try:
            self.generate_image()
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem changing avatar : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            if self.tmp:
                shutil.rmtree(self.tmp)
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def generate_image(self):
        self.tmp = generate_random_folder()
        image_path = self.template.download_image(self.tmp)

        self.image_path = process_image(image_path, self.tmp)

    def before_change_hook(self):

        self.base = BrowserBaseEvent(self.ig)
        self.ig.account.set_state('set avatar', 'app_state')
        self.command = self.ig.account.create_command('set avatar', 'processing')

    def change_hook(self):
        self.ig.page.goto('https://www.instagram.com/accounts/edit/')
        self.ig.pause(4000, 5000)

        self.ig.page.locator("input[accept='image/jpeg,image/png']").nth(0).set_input_files(
            self.image_path)
        self.ig.pause(19000, 20000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('avatar_changed', 1)
        self.ig.account.attach_template(self.template)
        self.ig.account.add_cli("Avatar changed successfully")
