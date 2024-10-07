from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.models.Template import get_a, delete


class BrowserChangeBioEvent(InstagramMiddleware):
    base = None
    command = 0
    bio = 0

    def execute(self):

        if self.ig.account.has('bio'):
            return self.ig.account.add_cli(f'{self.ig.account.username} has a bio')

        self.bio = get_a('bio', self.ig.account).text

        if not self.bio:
            return self.ig.account.add_cli(f"We don't have a bio for : {self.ig.account.username}")

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem changing bio : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        delete('bio', self.bio)

        self.ig.account.add_cli('Going to Accounts profile page')
        self.ig.page.goto('https://www.instagram.com/accounts/edit/')
        self.ig.pause(3000, 4000)
        self.ig.account.set_state('set bio', 'app_state')
        self.command = self.ig.account.create_command('set bio', 'processing')

    def change_hook(self):
        self.ig.page.locator('textarea[placeholder="Bio"]').fill(self.bio)
        self.ig.pause(2000, 3000)
        self.ig.page.locator('div[role="button"]:has-text("Submit")').click()
        self.ig.pause(2000, 3000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('bio', self.bio)
        self.ig.account.add_cli("Bio changed successfully")

