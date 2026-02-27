from script.extra.helper import go_to_page
from script.models.OrderAction import get_single_action_for_account, mark_action_completed, mark_action_failed, deduct_balance, OrderAction, ACTION_RATES
from script.models.Order import Order
from script.models.Balance import Balance
from script.models.Setting import Setting
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from urllib.parse import urlparse
from decimal import Decimal


class BrowserLikeAndCommentEvent(BaseAction):
    command = None
    action = None
    order = None
    processed_order_ids = []

    def init(self):
        if self.ig.account.get_passed_days_since_creation() < 2:
            return self.ig.account.add_cli(f"Account is not old enough to send comment")

        batch_size = int(Setting.get_value('comment_batch_size', 1))
        self.processed_order_ids = []

        for i in range(batch_size):
            action = get_single_action_for_account(
                self.ig.account,
                ['comment'],
                excluded_order_ids=self.processed_order_ids
            )

            if not action:
                if i == 0:
                    raise Exception('There is no comment order')
                break

            self.action = action
            self.order = action.order
            self.processed_order_ids.append(self.order.id)

            self.ig.account.add_cli(f'Picked action #{i+1} for order {self.order.id}', print_only=True)
            self.process_single_action()

    def process_single_action(self):
        if not self.action.content:
            self.ig.account.add_cli("No content for this action - skipping", print_only=True)
            self._safe_reset_to_free()
            return

        self.ig.account.add_cli(f'Order: {self.order.id} | Target: {self.order.target_link}', print_only=True)

        try:
            self.command = self.ig.account.create_command('comment and like', 'processing')
            self.post_url_validation()
            go_to_page(self.ig, self.order.target_link, 'Post Page')
            self.ig.pause(5000, 6000)
            self.dismiss_popup()
            self.ig.pause(1000, 1200)
            self.check_fail_situations()

            if 'reels' in self.ig.page.url:
                try:
                    self.ig.page.locator("svg[aria-label='Comment']").first.click(timeout=3000)
                    self.ig.pause(3000, 3500)
                except Exception as e:
                    self.ig.page.locator("div[role='button']").filter(
                        has=self.ig.page.locator("svg[aria-label='Comment']")).click()

            self.ig.page.get_by_placeholder("Add a comment…").fill(self.action.content, timeout=5000)
            self.ig.pause(1500, 2000)
            self.ig.page.get_by_role("button", name="Post", exact=True).click()
            self.ig.pause(1000, 1200)

            if self.ig.is_visible_by_text("Couldn't post comment"):
                raise Exception("Couldn't post comment")

            self.mark_action_sent()
            self.command.update_cmd('state', 'success')
            self.ig.account.add_cli('SUCCESS - Comment posted', print_only=True)
            self.ig.pause(3500, 4500)

        except LinkIsNotCorrect as e:
            self.ig.account.add_cli(f'FAILED - {str(e)}', print_only=True)
            self.fail_order_with_full_charge(str(e))

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.ig.account.add_cli(f'ERROR - {str(e)}', print_only=True)
            self._safe_reset_to_free()

            if self.command:
                self.command.update_cmd('state', 'fail')

    def _safe_reset_to_free(self):
        """Safely reset action to free status"""
        try:
            OrderAction.update(
                status='free',
                account=None
            ).where(
                (OrderAction.id == self.action.id) &
                (OrderAction.status == 'processing')
            ).execute()
        except Exception as e:
            self.ig.account.add_cli(f'Error resetting action: {e}', print_only=True)

    def fail_order_with_full_charge(self, message):
        """
        Fail the entire order and deduct balance for all actions.
        """
        try:
            updated = Order.update(
                status='Canceled',
                description=message
            ).where(
                (Order.id == self.order.id) &
                (Order.status != 'Canceled')
            ).execute()

            if updated == 0:
                return

            self.order.status = 'Canceled'

            OrderAction.update(
                status='failed'
            ).where(
                (OrderAction.order == self.order.id) &
                (OrderAction.status == 'free')
            ).execute()

            rate = ACTION_RATES.get(self.order.service_type, Decimal('0.0003'))
            total_charge = Decimal(self.order.total_count) * rate

            Balance.update(
                balance=Balance.balance - total_charge
            ).where(
                Balance.customer == 'sadeghi'
            ).execute()

        except Exception as e:
            self.ig.account.add_cli(f"Failed to charge order: {e}", print_only=True)

    def post_url_validation(self):
        parsed = urlparse(self.order.target_link)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            raise LinkIsNotCorrect("Invalid link, not an Instagram URL")

        path = parsed.path.strip('/').split('/')

        if len(path) == 1:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

        valid_first_segment = ["p", "reel", "tv"]

        if len(path) == 2 and path[0] in valid_first_segment:
            pass
        elif len(path) == 3 and path[1] in valid_first_segment:
            pass
        else:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

    def dismiss_popup(self):
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
            except:
                pass

    def check_fail_situations(self):
        if self.ig.is_visible_by_text('This account is private'):
            raise LinkIsNotCorrect('Account is private')

        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            raise LinkIsNotCorrect('Comments on this post have been limited')

        if self.ig.is_visible_by_text("Post isn't available") or \
           self.ig.is_visible_by_text("The link may be broken") or \
           self.ig.is_visible_by_text("the profile may have been removed"):
            raise LinkIsNotCorrect("Post isn't available")

        if self.ig.is_visible_by_text("Sorry, this page isn't available") or \
           self.ig.is_visible_by_text("Page is not available") or \
           self.ig.is_visible_by_text("This page isn't available"):
            raise LinkIsNotCorrect("Page is not available")

        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise Exception("Page load issue - temporary error")

        comment_locator = self.ig.page.locator('svg[aria-label="Comment"]').first
        like_locator = self.ig.page.locator('svg[aria-label="Like"]').first

        if like_locator.is_visible() and not comment_locator.is_visible():
            raise LinkIsNotCorrect("Comment box is not visible")

    def mark_action_sent(self):
        mark_action_completed(self.action)
        deduct_balance('comment')