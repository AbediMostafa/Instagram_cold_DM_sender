from script.models.Template import get_next
from script.extra.playwright.base_actions.GoToProfilePageAction import GoToProfilePageAction
from script.extra.helper import go_to_page
from script.extra.routes import *
from script.extra.actions.BaseAction import BaseAction


class BrowserChangeNameUsernameEvent(BaseAction):
    command = None
    name_username = None
    username = None
    name = None
    username_counter = 0

    def init(self):
        if self.ig.account.username_changed:
            return self.ig.account.add_cli(f"Account's username has been changed already.")

        if self.ig.account.get_passed_days_since_creation() < 4:
            return self.ig.account.add_cli(f"Account is not old enough to change name username")

        self.ig.account.add_cli('Changing name and username ...')

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()
            self.take_screenshot(command_name='set name username', command_id=self.command.id)

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')

            self.take_screenshot(command_name='set name username', command_id=self.command.id, fail_or_success='fail')

            self.ig.account.add_cli(f"Problem changing name : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.name_username = get_next('name-username')

        if not self.name_username:
            raise Exception(f"We dont have a name or username for this account")

        print(f'Name username id: {self.name_username.id}')

        self.username = self.name_username.text
        self.name = self.name_username.caption

        # self.ig.account.set_state('set name and username', 'app_state')
        self.command = self.ig.account.create_command('set name username', 'processing')

    def change_hook(self):

        GoToProfilePageAction(self.ig).start()

        try:
            self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click(timeout=3000)
        except Exception as e:
            self.ig.page.get_by_label(f"Profiles {self.ig.account.username}").click(timeout=3000)
            self.ig.pause(2000, 2500)
            self.ig.page.get_by_label(f"{self.ig.account.username} Instagram").click(timeout=3000)

        self.ig.pause(3000, 3500)
        self.ig.account.add_cli(f"Name appeared")
        self.ig.page.evaluate("""
        () => {
          const el = document.querySelector('a[aria-label="Name"]');
          if (el) el.click();
        }
        """)
        self.ig.account.add_cli(f"Name Clicked")

        self.ig.pause(3000, 4000)
        self.fill_name()
        self.ig.pause(4000, 5000)
        self.ig.page.evaluate("""
        () => {
          const el = document.querySelector('a[aria-label="Username"]');
          if (el) el.click();
        }
        """)
        self.ig.pause(3000, 4000)
        self.fill_username()

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('name', self.name)
        self.ig.account.set('username', self.username)
        self.ig.account.set('username_changed', 1)
        # res = delete_template([self.name_username['id']])
        # print(res)

    def fill_name(self):
        try:
            self.ig.page.locator("input#_r_l_").fill(self.name, timeout=3000)
            self.ig.account.add_cli("Problem filling first locator 'input#_r_l_'")
        except:
            self.ig.page.locator("div.x6s0dn4.x78zum5.x1qughib.xh8yej3 input[type='text']").first.fill(self.name,
                                                                                                       timeout=3000)
        self.ig.pause(3000, 4000)

        self.ig.page.get_by_role("button", name="Done").click(timeout=3000)
        self.ig.pause(4000, 5000)

    def fill_username(self):
        self.fill_locator()
        self.ig.pause(4000, 5000)

        while self.ig.is_visible_by_text('Username is not available'):
            self.ig.account.add_cli(f'Selected username is not available')
            self.modify_username()
            self.fill_locator()
            self.username_counter += 1
            self.ig.pause(4000, 5000)

            if self.username_counter >= 10:
                raise Exception('6 Times username exists exceeded')

        self.ig.page.get_by_role("button", name="Done").click(timeout=5000)
        self.ig.pause(4000, 5000)

    def fill_locator(self):

        try:
            self.ig.page.locator("input[type='text']").first.fill(self.username, timeout=5000)
            self.ig.account.add_cli("First input selector (input[type='text']) not available")
        except:

            try:
                self.ig.page.locator("input#_r_m_").fill(self.username, timeout=5000)
                self.ig.account.add_cli("Second input selector (input#_r_m_) not available")
            except:
                self.ig.page.locator("div.x6s0dn4.x78zum5.x1qughib.xh8yej3 input[type='text']").nth(0).fill(
                    self.username, timeout=5000)

    def modify_username(self):
        import random
        import string

        char = random.choice(string.ascii_lowercase)
        digit = str(random.randint(0, 9))

        # insert_char = random.choice(['_', '.', char, digit])
        pos = random.randint(1, len(self.username) - 1)  # not first, not last
        self.username = self.username[:pos] + char + self.username[pos:]
