import traceback
from script.extra.helper import go_to_page

from script.models.Account import Account


class BrowserAccountStatusCheckerEvent:
    number_of_accounts_to_check = 15
    command = None
    account_to_check = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        for _ in range(self.number_of_accounts_to_check):
            try:
                self.find_account_to_check()

                if not self.account_to_check:
                    self.ig.account.add_cli("No accounts found to check")
                    return

                self.before_check_hook()

                self.check_account_status()
                self.ig.pause(3000, 4000)

                self.after_check_hook()

            except Exception as e:
                self.handle_failure(e)

            finally:
                self.ig.pause(3000, 4000)

    def before_check_hook(self):
        self.command = self.ig.account.create_command('account_status_check', 'processing')

    def after_check_hook(self):
        self.command.update_cmd('state', 'success')

    def handle_failure(self, error):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.ig.account.add_cli(f"Account status check failed: {str(error)}")
        self.ig.account.add_log(traceback.format_exc())

    def find_account_to_check(self):
        self.account_to_check = (Account
                                 .select()
                                 .where(
            (Account.instagram_state.in_(['suspended', 'challenging'])) &
            (Account.is_used == 0)
        )
                                 .order_by(Account.id.asc())
                                 .first())

        if self.account_to_check:
            self.account_to_check.is_used = 1
            self.account_to_check.save()

    def check_account_status(self):
        self.ig.account.add_cli(f"Checking account: {self.account_to_check.username} (ID: {self.account_to_check.id})")

        profile_url = f"https://www.instagram.com/{self.account_to_check.username}/"
        go_to_page(self.ig, profile_url, 'Account page')

        self.ig.pause(3000, 4000)

        if self.is_profile_unavailable():
            self.ig.account.add_cli(
                f"UNAVAILABLE: {self.account_to_check.username} (ID: {self.account_to_check.id}) - Profile is banned")
            self.handle_unavailable_account()
        else:
            self.ig.account.add_cli(
                f"AVAILABLE: {self.account_to_check.username} (ID: {self.account_to_check.id}) - Profile exists")

    def is_profile_unavailable(self):
        unavailable_texts = [
            "Profile isn't available",
            "The link may be broken, or the profile may have been removed",
            "Sorry, this page isn't available.",
            "The link you followed may be broken, or the page may have been removed.",
        ]

        for text in unavailable_texts:
            if self.ig.is_visible_by_text(text):
                return True

        return False

    def handle_unavailable_account(self):
        username = self.account_to_check.username
        account_id = self.account_to_check.id

        self.account_to_check.delete_instance()
        self.ig.account.add_cli(f"DELETED: {username} (ID: {account_id}) - Removed from database")
