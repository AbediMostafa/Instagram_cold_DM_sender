from script.extra.helper import go_to_page

class BrowserMakeAccountPublicEvent:
    command = None

    def __init__(self, ig):
        self.ig = ig
        self.category_model = self.ig.account.category

    def init(self):
        self.ig.account.add_cli('Making account public...')

        try:
            self.command = self.ig.account.create_command(
                'make public',
                'processing',
                category=self.category_model)

            self.change_hook()
            self.ig.account.set('is_public', 1)
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')

            self.ig.account.add_cli(f"Problem making account public : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            go_to_page(self.ig, 'https://www.instagram.com/', "Home")

            self.ig.pause(3000, 4000)
        pass

    def change_hook(self):

        try:
            go_to_page(self.ig, f'https://www.instagram.com/{self.ig.account.username}', "User")

            self.ig.pause(4000, 4500)
            self.ig.page.get_by_role("button", name="Options").click()

            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("button", name="Settings and privacy").click()

            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("link", name="Account privacy").click()

        except:
            go_to_page(self.ig, 'https://www.instagram.com/accounts/settings/v2/account_privacy/', "Account Privacy")


        self.ig.pause(4000, 5000)

        checkbox_locator = self.ig.page.locator('input[role="switch"]')
        is_checked = checkbox_locator.get_attribute('aria-checked')

        self.ig.account.add_cli(f'Account is private : {is_checked}')

        if is_checked == 'false':
            return self.ig.account.add_cli(f'Account is private')

        try:
            checkbox_locator.click(timeout=3000)
        except:
            self.ig.page.get_by_label("Private account").uncheck()

        self.ig.pause(4000, 5000)
        self.ig.page.get_by_role("button", name="Switch to public").click()

        self.ig.pause(8000, 9000)
