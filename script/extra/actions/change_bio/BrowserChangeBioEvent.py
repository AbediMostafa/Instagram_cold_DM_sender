from script.extra.helper import go_to_page
from script.models.Template import get_next
from script.models.Lead import Lead


class BrowserChangeBioEvent:
    command = None
    bio = None
    lead = None

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
        self.bio, self.lead = Lead.get_a_template(self.ig.account, 'bio')

        if not self.bio:
            raise Exception(f'No bio ...')

        self.bio = self.bio.text

    def before_change_hook(self):

        self.ig.account.add_cli('Going to Accounts profile page')
        self.command = self.ig.account.create_command('set bio', 'processing')
        go_to_page(self.ig, "https://www.instagram.com/accounts/edit/", "Edit page")
        self.ig.pause(3000, 4000)

    def change_hook(self):

        self.ig.page.locator('textarea[placeholder="Bio"]').fill(self.bio)
        self.ig.pause(2000, 3000)

        counter_locator = self.ig.page.locator("#pepBio").locator("xpath=ancestor::div[1]//span[contains(text(), '/')]")

        counter_text = counter_locator.inner_text()

        print(f'counter_text : {counter_text}')

        current, max_len = map(int, counter_text.split('/'))
        counter = 0

        if current > max_len:

            # trim progressively until it fits
            while current > max_len:

                counter += 1
                self.ig.account.add_cli(
                    f'Your bio length {current} is more than allowed {max_len}, trying to trim for the {counter} time ...')

                self.bio = self.bio[:-2]  # remove last two character
                self.ig.page.locator('textarea[placeholder="Bio"]').fill(self.bio)
                self.ig.pause(1000, 1100)

                counter_text = counter_locator.inner_text()
                current, max_len = map(int, counter_text.split('/'))

                if counter >= 40:
                    break

        self.ig.pause(1000, 10000)

        self.ig.page.locator('div[role="button"]:has-text("Submit")').click()
        self.ig.pause(5000, 5500)

        if self.ig.is_visible_by_text('There was a problem saving'):
            raise Exception('There was a problem saving your profile')

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('bio', self.bio)

        if self.lead.account is None:
            self.lead.set_account(self.ig.account)

        self.ig.account.add_cli("Bio changed successfully")
