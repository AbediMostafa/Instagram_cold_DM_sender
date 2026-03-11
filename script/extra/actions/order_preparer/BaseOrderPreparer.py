import time
import traceback
from datetime import timedelta
from decimal import Decimal

from script.extra.helper import tehran_now
from script.extra.actions.BaseAction import BaseAction
from script.models.Order import Order
from script.models.OrderAction import OrderAction, ACTION_RATES, deduct_balance
from script.models.Balance import Balance
from script.models.Setting import Setting


STUCK_TIMEOUT_SECONDS = 120
CAPTURE_TIMEOUT_SECONDS = 30

SUPPORTED_SERVICE_TYPES = ['view_story', 'save_post']



class BaseOrderPreparer(BaseAction):
    """Base class for preparing orders with shared methods"""

    order = None
    captured_data = None
    listeners = []

    def init(self):
        self._reset_stuck_orders()

        batch_size = int(Setting.get_value('order_prepare_batch_size', 3))

        for i in range(batch_size):
            order = self._claim_next_order()

            if not order:
                if i == 0:
                    self.ig.account.add_cli('No orders to prepare')
                break

            self.order = order
            self.captured_data = None
            self.listeners = []

            self.ig.account.add_cli(f'Preparing order #{order.id} ({order.service_type}): {order.target_link}')

            try:
                self._process_order()
            except Exception as e:
                self.ig.account.add_cli(f'Error processing order #{order.id}: {str(e)}')
                self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')

    def _reset_stuck_orders(self):
        """Reset orders stuck in preparing state (is_prepared=1)"""
        cutoff_time = tehran_now() - timedelta(seconds=STUCK_TIMEOUT_SECONDS)

        updated = Order.update(
            is_prepared=0
        ).where(
            (Order.is_prepared == 1) &
            (Order.service_type.in_(SUPPORTED_SERVICE_TYPES)) &
            (Order.updated_at < cutoff_time)
        ).execute()

        if updated > 0:
            self.ig.account.add_cli(f'Reset {updated} stuck orders')

    def _claim_next_order(self):
        """Find and claim next order using atomic UPDATE"""
        candidate = (
            Order
            .select(Order.id)
            .where(
                (Order.service_type.in_(SUPPORTED_SERVICE_TYPES)) &
                (Order.is_prepared == 0) &
                (Order.status == 'Pending')
            )
            .order_by(Order.id.asc())
            .first()
        )

        if not candidate:
            return None

        updated = Order.update(
            is_prepared=1,
            updated_at=tehran_now()
        ).where(
            (Order.id == candidate.id) &
            (Order.is_prepared == 0)
        ).execute()

        if updated == 0:
            return None

        return Order.get_by_id(candidate.id)

    def _process_order(self):
        """Route to appropriate handler based on service_type"""
        try:
            if self.order.service_type == 'view_story':
                from .handlers.StoryPrepareHandler import StoryPrepareHandler
                handler = StoryPrepareHandler(self.ig, self)
                handler.prepare(self.order)

            elif self.order.service_type == 'save_post':
                from .handlers.SavePostPrepareHandler import SavePostPrepareHandler
                handler = SavePostPrepareHandler(self.ig, self)
                handler.prepare(self.order)

            else:
                raise Exception(f'Unknown service_type: {self.order.service_type}')

            if not self.captured_data:
                raise Exception('Failed to capture data')

            self._save_action_data()
            self._create_order_actions()
            self.ig.account.add_cli(f'Order #{self.order.id} prepared successfully')

        except TimeoutError as e:
            self._handle_timeout(str(e))

        except RetryableError as e:
            self._handle_timeout(str(e))
            self._log_to_file(f'RETRYABLE: {str(e)}', 'retry')

        except Exception as e:
            self._handle_error(str(e))
            self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')

        finally:
            self._cleanup_listeners()
            self._force_exit()

    def _save_action_data(self):
        """Save captured data to order and mark as prepared"""
        Order.update(
            is_prepared=2,
            action_data=self.captured_data,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _create_order_actions(self):
        """Create OrderAction records - first one as sent, rest as free"""
        # First action - preparer's action
        OrderAction.create(
            order_id=self.order.id,
            type=self.order.service_type,
            status='sent',
            account=self.ig.account
        )

        Order.update(completed_count=1).where(Order.id == self.order.id).execute()
        deduct_balance(self.order.service_type)

        # Remaining actions
        remaining_count = self.order.total_count - 1

        if remaining_count > 0:
            actions = [
                {'order_id': self.order.id, 'type': self.order.service_type, 'status': 'free'}
                for _ in range(remaining_count)
            ]
            OrderAction.insert_many(actions).execute()

        self.ig.account.add_cli(f'Created 1 sent + {remaining_count} free actions')

    def _handle_timeout(self, message):
        """Handle timeout - reset for retry"""
        self.ig.account.add_cli(f'Order #{self.order.id} timeout: {message}')

        Order.update(
            is_prepared=0,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _handle_error(self, message):
        """Handle error - cancel order and charge full amount"""
        self.ig.account.add_cli(f'Order #{self.order.id} failed: {message}')

        Order.update(
            status='Canceled',
            is_prepared=0,
            description=message,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

        self._charge_full_order()

    def _charge_full_order(self):
        """Deduct full order amount from balance"""
        rate = ACTION_RATES.get(self.order.service_type, Decimal('0.00005'))
        total_charge = Decimal(self.order.total_count) * rate

        Balance.update(
            balance=Balance.balance - total_charge
        ).where(
            Balance.customer == 'sadeghi'
        ).execute()

        self.ig.account.add_cli(f'Charged ${total_charge}')

    def _cleanup_listeners(self):
        """Remove all registered listeners"""
        for listener in self.listeners:
            try:
                self.ig.page.remove_listener('response', listener)
            except:
                pass
        self.listeners = []

    def _force_exit(self):
        """Exit current view (story/post)"""
        try:
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(300, 500)
        except:
            pass

    def _log_to_file(self, message, log_type='info'):
        """Log to file for debugging"""
        try:
            import os

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'order_preparer.log')

            order_id = self.order.id if self.order else 'N/A'
            account_id = self.ig.account.id if self.ig.account else 'N/A'
            service_type = self.order.service_type if self.order else 'N/A'
            link = self.order.target_link if self.order else 'N/A'

            log_line = f'[{tehran_now()}] [{log_type.upper()}] order={order_id} | type={service_type} | account={account_id} | link={link} | {message}\n'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass

    def wait_for_capture(self, timeout=CAPTURE_TIMEOUT_SECONDS):
        """Wait for data to be captured"""
        start = time.time()

        while time.time() - start < timeout:
            if self.captured_data:
                return True
            time.sleep(0.3)

        raise TimeoutError('Timeout waiting for data capture')