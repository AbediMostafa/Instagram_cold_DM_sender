from script.extra.helper import go_to_page
from script.models.Order import get_next_order_for_account
from script.models.OrderComment import get_next_comment_for_order
from script.extra.helper import tehran_now
from script.extra.exceptions import LinkIsNotCorrect


class BrowserCommentEvent:
    command = None
    comment = None
    account_age = None
    order = None

    def __init__(self, ig):

        self.ig = ig
        self.account_age = self.ig.account.get_passed_days_since_creation()

    def pick_and_mark_comment(self):
        # Step 1: find available order
        self.order = get_next_order_for_account(self.ig.account)
        if not self.order:
            raise Exception('There is no order')

        self.ig.account.add_cli(f'selected order: {self.order.id}', print_only=True)
        self.ig.account.add_cli(f'selected order: {self.order.target_link}', print_only=True)

        if self.order.status_is("Pending"):
            self.order.set_status_to("In progress")

        # Step 2: pick a free comment
        self.comment = get_next_comment_for_order(self.order)

        if not self.comment:
            raise Exception('There is no comment for this account')

    def init(self):

        if self.ig.account.get_passed_days_since_creation() < 15:
            return self.ig.account.add_cli(f"Account is not old enough to Send comment")

        self.pick_and_mark_comment()
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

            self.ig.page.get_by_placeholder("Add a comment…").fill(self.comment.content)
            self.ig.pause(4000, 5000)
            self.ig.page.get_by_role("button", name="Post").click()

            self.mark_comment_sent()
            self.command.update_cmd('state', 'success')
            self.ig.pause(4000, 5000)

        except LinkIsNotCorrect as e:
            self.ig.account.add_cli(str(e), print_only=True)
            self.order.set_status_to("Cancel")

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.ig.account.add_cli(str(e), print_only=True)

            self.comment.set_status_to('free')

            if self.command:
                self.command.update_cmd('state', 'fail')

    def go_to_page(self):

        try:
            go_to_page(self.ig, self.order.target_link, 'Post Page')
        except Exception as e:
            raise LinkIsNotCorrect(str(e))

    def check_fail_situations(self):
        if self.ig.is_visible_by_text('This account is private'):
            self.order.fail('Account is private')
            raise Exception('Account is private')

        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            self.order.fail('Comments on this post have been limited')
            raise Exception('Comments on this post have been limited')

        if self.ig.is_visible_by_text("Post isn't available") or self.ig.is_visible_by_text(
                "The link may be broken") or self.ig.is_visible_by_text("the profile may have been removed"):
            self.order.fail("Post isn't available")
            raise Exception("Post isn't available")

    def mark_comment_sent(self):
        self.comment.set_status_to('sent')
        self.order.add_completed_count()
        self.order.make_order_completed()
