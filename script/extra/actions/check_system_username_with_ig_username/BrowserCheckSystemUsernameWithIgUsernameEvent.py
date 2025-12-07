import re
from script.extra.helper import go_to_page


class BrowserCheckSystemUsernameWithIgUsernameEvent:
    command = None
    username = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        self.ig.account.add_cli('Checking username with IG username...')

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem Finding Username match : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")

            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.command = self.ig.account.create_command('username match', 'processing')

    def change_hook(self):
        self.click_on_profile()
        self.ig.pause(3000, 4000)
        self.get_username()

        if self.username.lower() == self.ig.account.username.lower():
            return self.ig.account.add_cli('Username match ...')

        self.click_on_options()
        self.ig.pause(3500, 4500)

        self.ig.page.get_by_role("button", name=re.compile(r"log out", re.I)).click(timeout=4000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')

    def click_on_profile(self):
        try:
            self.ig.page.get_by_role("link").filter(has=self.ig.page.locator('span[role="link"]')).first.click()
        except Exception as e:
            self.ig.account.add_cli('Couldnt click on Profile trying second way ...')

            try:
                self.ig.page.locator("text=Profile").first.click(timeout=4500)
            except Exception as e:
                self.ig.account.add_cli('Couldnt click on text=Profile trying third way ...')
                self.ig.page.get_by_role("link", name="Profile").click(timeout=4500)

    def get_username(self):

        try:
            locator = self.ig.page.locator('h2 span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft')
            locator.wait_for(state='visible', timeout=5000)
            self.username = locator.inner_text(timeout=3000)

            self.ig.account.add_cli(f'IG username : {self.username}')
        except:
            self.ig.account.add_cli('Couldnt get username trying second way ...')
            locator = self.ig.page.locator('h1 span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft')
            locator.wait_for(state='visible', timeout=5000)
            self.username = locator.inner_text(timeout=3000)

    def click_on_options(self):

        try:
            self.ig.page.get_by_role("button", name="Options").click(timeout=4500)
        except Exception as e:
            self.ig.account.add_cli('Couldnt click on Options trying second way ...')
            self.ig.page.locator('svg[aria-label="Options"]').click(timeout=4500)
