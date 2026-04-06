import traceback
import os
from datetime import datetime
from script.extra.helper import go_to_page
from script.models.Account import Account


class BrowserAccountStatusCheckerEvent:
    number_of_accounts_to_check = 3
    command = None
    account_to_check = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        for _ in range(self.number_of_accounts_to_check):
            self.command = None
            self.account_to_check = None

            try:
                self.find_account_to_check()

                if not self.account_to_check:
                    self.ig.account.add_cli("No accounts found to check")
                    return

                self.before_check_hook()

                is_unavailable = self.check_account_status()
                self.ig.pause(3000, 4000)

                self.after_check_hook()

                # if is_unavailable:
                #     return

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
        account = (Account
                   .select()
                   .where(
            (Account.instagram_state.in_(['suspended', 'challenging'])) &
            (Account.is_used == 0)
        )
                   .order_by(Account.id.asc())
                   .first())

        if not account:
            return

        # Atomic claim - only one thread wins
        updated = (Account
                   .update(is_used=1)
                   .where(
            (Account.id == account.id) &
            (Account.is_used == 0)
        )
                   .execute())

        if updated:
            account.is_used = 1
            self.account_to_check = account

    def check_account_status(self):
        """Check if account profile is available. Returns True if unavailable (deleted)."""
        self.ig.account.add_cli(f"Checking account: {self.account_to_check.username} (ID: {self.account_to_check.id})")

        profile_url = f"https://www.instagram.com/{self.account_to_check.username}/"
        go_to_page(self.ig, profile_url, 'Account page')

        self.ig.pause(3000, 4000)

        if self.is_profile_unavailable():
            self.ig.account.add_cli(
                f"UNAVAILABLE: {self.account_to_check.username} (ID: {self.account_to_check.id}) - Profile is banned")
            self.delete_account(self.account_to_check)
            return True

        self.ig.account.add_cli(
            f"AVAILABLE: {self.account_to_check.username} (ID: {self.account_to_check.id}) - Profile exists")
        return False

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

    def delete_account(self, account):
        username = account.username
        account_id = account.id
        db = Account._meta.database

        self._log_to_file(f"Starting delete for: {username} (ID: {account_id})")

        try:
            with db.atomic():
                db.execute_sql("SET LOCAL lock_timeout = '30s'")
                account.delete_instance()

            self._log_to_file(f"DELETED: {username} (ID: {account_id})")
            self.ig.account.add_cli(f"DELETED: {username} (ID: {account_id})")
        except Exception as e:
            self._log_to_file(f"DELETE FAILED: {username} (ID: {account_id}) - {str(e)}", 'error')
            self.ig.account.add_cli(f"DELETE FAILED: {username} (ID: {account_id}) - {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

    def _log_to_file(self, message, log_type='info'):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'account_status_checker.log')

            account_id = self.ig.account.id if self.ig.account else 'N/A'
            target_id = self.account_to_check.id if self.account_to_check else 'N/A'

            log_line = f'[{datetime.now()}] [{log_type.upper()}] checker_account={account_id} | target={target_id} | {message}\n'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass