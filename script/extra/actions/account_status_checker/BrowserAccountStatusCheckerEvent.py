import traceback

from script.models.Account import Account


class BrowserAccountStatusCheckerEvent:
    accounts_to_check = []
    command = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        try:
            self.find_accounts_to_check()

            if not self.accounts_to_check:
                self.ig.account.add_cli("No accounts found to check")
                return

            self.before_check_hook()

            for account in self.accounts_to_check:
                self.check_account_status(account)
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
        self.ig.account.add_cli("Account status check completed")

    def handle_failure(self, error):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.ig.account.add_cli(f"Account status check failed: {str(error)}")
        self.ig.account.add_log(traceback.format_exc())

    def find_accounts_to_check(self):
        self.accounts_to_check = (Account
            .select()
            .where(
                (Account.instagram_state.in_(['suspended', 'challenging'])) &
                (Account.is_used == 0)
            )
            .order_by(Account.id.asc())
            .limit(5))

    def check_account_status(self, account):
        self.ig.account.add_cli(f"Checking account: {account.username} (ID: {account.id})")

        profile_url = f"https://www.instagram.com/{account.username}/"
        self.go_to_profile(profile_url)

        self.ig.pause(3000, 4000)

        if self.is_profile_unavailable():
            self.ig.account.add_cli(f"UNAVAILABLE: {account.username} (ID: {account.id}) - Profile is banned")
            self.handle_unavailable_account(account)
        else:
            self.ig.account.add_cli(f"AVAILABLE: {account.username} (ID: {account.id}) - Profile exists")
            self.handle_available_account(account)

    def go_to_profile(self, url):
        self.ig.page.goto(url)

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

    def handle_unavailable_account(self, account):
        username = account.username
        account_id = account.id

        account.delete_instance()

        self.ig.account.add_cli(f"DELETED: {username} (ID: {account_id}) - Removed from database")

    def handle_available_account(self, account):
        account.is_used = 1
        account.save()
        self.ig.account.add_cli(f"Marked as exist: {account.username} (ID: {account.id})")