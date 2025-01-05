from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware


class BrowserMakeAccountPublic(InstagramMiddleware):
    base = None
    command = 0

    def execute(self):

        if self.ig.account.is_public:
            return self.ig.account.add_cli(f"Account is public")

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            self.ig.account.add_cli(f"Problem making account public : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.ig.account.add_cli('Going to Setting page')

    def change_hook(self):

        try:
            try:
                self.ig.page.get_by_role("link", name=f"{self.ig.account.username}'s profile picture Profile").click()
            except:
                self.ig.page.goto(f'https://www.instagram.com/{self.ig.account.username}')

            self.ig.pause(4000, 4500)
            self.ig.page.get_by_role("button", name="Options").click()

            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("button", name="Settings and privacy").click()

            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("link", name="Account privacy").click()

        except:
            self.ig.page.goto('https://www.instagram.com/accounts/settings/v2/account_privacy/')

        self.ig.pause(4000, 5000)

        checkbox_locator = self.ig.page.locator('input[role="switch"]')
        is_checked = checkbox_locator.get_attribute('aria-checked')

        self.ig.account.add_cli(f'Account is private {is_checked}')

        if is_checked == 'true':
            self.ig.account.add_cli(f'Account is private')

            try:
                checkbox_locator.click(timeout=3000)
            except:
                self.ig.page.get_by_label("Private account").uncheck()

            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("button", name="Switch to public").click()

        self.ig.pause(6000, 7000)

    def after_change_hook(self):
        self.ig.account.set('is_public', 1)

