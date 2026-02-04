from script.models.Template import get_a
from script.extra.playwright.base_actions.GoToProfilePageAction import GoToProfilePageAction
from script.extra.helper import go_to_page
from script.extra.routes import get_template


class BrowserChangeBioEvent:
    command = None
    bio = None

    def __init__(self, ig):
        self.ig = ig

        if self.ig.account.has('bio'):
            raise Exception(f'{self.ig.account.username} has a bio')

        if self.ig.account.get_passed_days_since_creation() < 3:
            raise Exception(f"Account is not old enough to set bio")

    def init(self):
        self.ig.account.add_cli('Changing bio ...')

        try:
            self.get_bio()
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
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")
            self.ig.pause(3000, 4000)

    def get_bio(self):
        self.bio = get_template(self.ig.account.id, 'bio')

        if not self.bio:
            raise Exception(f'No bio ...')

        self.bio = self.bio['text']

    def before_change_hook(self):

        self.ig.account.add_cli('Going to Accounts profile page')
        self.command = self.ig.account.create_command('set bio', 'processing')
        go_to_page(self.ig, "https://www.instagram.com/accounts/edit/", "Edit page")
        self.ig.pause(3000, 4000)
        self.ig.account.set_state('set bio', 'app_state')

    def change_hook(self):

        self.ig.page.locator('textarea[placeholder="Bio"]').fill(self.bio)
        self.ig.pause(3000, 4000)
        self.ig.page.locator('div[role="button"]:has-text("Submit")').click()
        self.ig.pause(5000, 5500)

        if self.ig.is_visible_by_text('There was a problem saving'):
            raise Exception('There was a problem saving your profile')

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('bio', self.bio)
        self.ig.account.add_cli("Bio changed successfully")
