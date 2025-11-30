from script.models.Template import get_a
from script.extra.playwright.base_actions.GoToProfilePageAction import GoToProfilePageAction
from script.extra.helper import go_to_page


class BrowserChangeNameUsernameEvent:
    command = None

    def __init__(self, ig):
        self.ig = ig
        self.name = get_a('name', self.ig.account)

        if not self.name:
            raise Exception(f"We dont have a name for this account")

    def init(self):
        self.ig.account.add_cli('Changing name ...')

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
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.ig.account.set_state('set name', 'app_state')
        self.command = self.ig.account.create_command('set name', 'processing')

    def change_hook(self):

        GoToProfilePageAction(self.ig).start()

        try:
            self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click(timeout=3000)
        except Exception as e:
            self.ig.page.get_by_label(f"Profiles {self.ig.account.username}").click(timeout=3000)
            self.ig.pause(2000, 2500)
            self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click(timeout=3000)

        self.ig.pause(3000, 4000)

        try:
            self.ig.page.get_by_label("Name", exact=True).click(timeout=3000)
        except Exception as e:
            self.ig.account.add_cli(str(e))
            self.ig.page.locator('a[aria-label="Name"]').click()

        self.ig.pause(3000, 4000)
        self.fill_name()
        self.ig.pause(4000, 5000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('name', self.name.text)

    def fill_name(self):
        self.fill_locator()
        self.ig.pause(3000, 4000)

        self.ig.page.get_by_role("button", name="Done").click(timeout=3000)
        self.ig.pause(4000, 5000)

    def fill_locator(self):

        try:
            self.ig.page.locator("input#_r_l_").fill(self.name.text, timeout=3000)
            self.ig.account.add_cli("Problem filling first locator 'input#_r_l_'")
        except:
            self.ig.page.locator("div.x6s0dn4.x78zum5.x1qughib.xh8yej3 input[type='text']").first.fill(self.name.text, timeout=3000)


