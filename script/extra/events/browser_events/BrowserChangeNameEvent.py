from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import random
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Template import get_a, delete


class BrowserChangeNameEvent(InstagramMiddleware):
    base = None
    name = "Edward Air"
    username_counter = 0
    command = 0

    def execute(self):

        if self.ig.account.has('name'):
            return self.ig.account.add_cli(f"Account has a name already.")

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem changing name : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.base = BrowserBaseEvent(self.ig)
        self.ig.account.set_state('set name', 'app_state')
        self.command = self.ig.account.create_command('set name', 'processing')

    def change_hook(self):

        self.base.go_to_profile_page()
        self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click()
        self.ig.page.locator('a[aria-label="Name"]').click()
        self.ig.pause(3000, 4000)

        self.fill_name()
        self.ig.pause(4000, 5000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('name', self.name)

    def fill_name(self):
        self.ig.page.get_by_label("Name").fill(self.name)
        self.ig.pause(3000, 4000)

        self.ig.page.get_by_role("button", name="Done").click(timeout=5000)
        self.ig.pause(4000, 5000)
