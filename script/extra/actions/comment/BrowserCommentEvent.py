from script.extra.helper import go_to_page
from script.models.OrderAction import get_next_action_for_account, mark_action_completed, mark_action_failed, deduct_balance
from script.extra.helper import tehran_now
from script.extra.exceptions import LinkIsNotCorrect


class BrowserCommentEvent:
    command = None
    action = None
    account_age = None
    order = None

    def __init__(self, ig):

        self.ig = ig
        self.account_age = self.ig.account.get_passed_days_since_creation()

    def pick_and_mark_action(self):
        # Step 1: find available action
        self.action = get_next_action_for_account(self.ig.account, ['comment'])
        if not self.action:
            raise Exception('There is no order')

        self.order = self.action.order

        self.ig.account.add_cli(f'selected order: {self.order.id}', print_only=True)
        self.ig.account.add_cli(f'selected order: {self.order.target_link}', print_only=True)

        if self.order.status == "Pending":
            self.order.set_status_to("In progress")

    def init(self):

        if self.ig.account.get_passed_days_since_creation() < 15:
            return self.ig.account.add_cli(f"Account is not old enough to Send comment")

        self.pick_and_mark_action()
        self.ig.account.add_cli('Starting to comment ...')

        try:
            self.command = self.ig.account.create_command('comment post', 'processing')
            self.go_to_page()
            self.ig.pause(4000, 5000)

            self.check_fail_situations()

            try:
                self.ig.page.get_by_role("button", name="Not now").click(timeout=3000)
            except Exception as e:
                self.ig.account.add_cli(str(e))

            self.ig.pause(1000, 1200)

            self.ig.page.get_by_placeholder("Add a comment…").fill(self.action.content)
            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("button", name="Post").click()

            self.mark_action_sent()
            self.command.update_cmd('state', 'success')
            self.ig.pause(4000, 5000)

        except LinkIsNotCorrect as e:
            # Client error - CHARGE but mark as FAILED
            self.ig.account.add_cli(str(e), print_only=True)
            self.mark_action_failed_with_charge()

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            # Server error - DON'T CHARGE
            self.ig.account.add_cli(str(e), print_only=True)

            self.action.reset_to_free()

            if self.command:
                self.command.update_cmd('state', 'fail')

    def go_to_page(self):

        try:
            go_to_page(self.ig, self.order.target_link, 'Post Page')
        except Exception as e:
            raise LinkIsNotCorrect(str(e))

    def check_fail_situations(self):
        if self.ig.is_visible_by_text('This account is private'):
            raise LinkIsNotCorrect('Account is private')

        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            raise LinkIsNotCorrect('Comments on this post have been limited')

        if self.ig.is_visible_by_text("Post isn't available") or self.ig.is_visible_by_text(
                "The link may be broken") or self.ig.is_visible_by_text("the profile may have been removed"):
            raise LinkIsNotCorrect("Post isn't available")

    def mark_action_sent(self):
        mark_action_completed(self.action)
        deduct_balance('comment')


    def mark_action_failed_with_charge(self):
        mark_action_failed(self.action)
        deduct_balance('comment')
