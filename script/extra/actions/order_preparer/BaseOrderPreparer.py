import time
import traceback
from datetime import timedelta

from script.extra.helper import tehran_now
from script.extra.actions.BaseAction import BaseAction
from script.extra.exceptions import RetryableError
from script.models.Order import Order
from script.models.OrderAction import OrderAction
from script.models.Balance import Balance
from script.models.Setting import Setting


# Time limit for orders stuck in is_prepared=1 (being prepared) state
# After this, they're reset to is_prepared=0 for another thread to try
STUCK_TIMEOUT_SECONDS = 120

# Maximum time to wait for browser to capture GraphQL data
CAPTURE_TIMEOUT_SECONDS = 45

# Service types that can be prepared by this class
SUPPORTED_SERVICE_TYPES = ['view_story', 'save_post', 'comment']


class BaseOrderPreparer(BaseAction):
    """
    Base class for preparing orders before API execution.

    The "prepare" phase does several things:
    1. Navigates to the target (story/post) via browser
    2. Captures GraphQL request data (doc_id, media_id, etc.) from network requests
    3. Performs the first action via browser (to validate everything works)
    4. Saves captured data to order.action_data for API execution phase
    5. Creates OrderAction records for remaining actions

    This approach allows us to:
    - Verify the target exists and is accessible before processing
    - Capture necessary data for direct API calls (faster than browser automation)
    - Handle the first action immediately while setting up for batch API execution

    Error handling:
    - TimeoutError/RetryableError: Reset order for another thread to try
    - Other errors: Cancel order and charge client (likely their fault - bad link, private account)

    Re-prepare scenario:
    When an order comes back from execution phase (after MAX_RETRY_ATTEMPTS failed),
    we need to handle existing OrderAction records and completed_count properly.
    """

    def __init__(self, ig):
        """
        Initialize instance variables.

        These must be on the instance (not the class) to prevent sharing
        between concurrent instances. In particular, 'listeners' is a mutable
        list — defining it on the class would cause all instances to share
        the same list, leading to cross-contamination bugs.
        """
        super().__init__(ig)
        self.order = None
        self.captured_data = None
        self.listeners = []

    def init(self):
        """
        Main entry point for the order preparer.

        Flow:
        1. Reset any stuck orders (is_prepared=1 for too long)
        2. Claim and process orders in batch based on settings
        """
        # First, clean up any orders that got stuck during preparation
        self._reset_stuck_orders()

        # Get batch size from settings
        batch_size = int(Setting.get_value('order_prepare_batch_size', 3))

        # Process orders in batch
        for i in range(batch_size):
            order = self._claim_next_order()

            if not order:
                if i == 0:
                    self.ig.account.add_cli('No orders to prepare')
                break

            # Reset instance variables for each order
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
        """
        Reset orders that have been stuck in preparing state too long.

        Orders with is_prepared=1 are being actively prepared by some thread.
        If they stay in this state too long, the thread probably crashed.
        Reset them to is_prepared=0 so another thread can try.

        Uses Lock to prevent all threads from running this same UPDATE
        every time init() is called. Only one thread per 60 seconds will
        actually execute the reset — the rest skip it immediately.
        """
        from script.models.Lock import Lock

        if not Lock.acquire('order_stuck_reset', duration_seconds=60):
            return

        try:
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

        finally:
            Lock.release('order_stuck_reset')

    def _claim_next_order(self):
        """
        Find and claim the next order to prepare using atomic UPDATE.

        Uses multi-candidate approach to handle thread contention:
        1. Find several candidate orders (not just one)
        2. Try to update is_prepared from 0 to 1 atomically for each
        3. If update succeeds (affected rows > 0), we own it
        4. If update fails, another thread got it first — try the next candidate

        Without multi-candidate, when 10 threads all see the same first order,
        only 1 succeeds and the other 9 return None even though more orders
        are available. This wastes processing cycles.

        Returns:
            Order instance or None if no orders available
        """
        # Find oldest pending orders that need preparation
        candidates = list(
            Order
            .select(Order.id)
            .where(
                (Order.service_type.in_(SUPPORTED_SERVICE_TYPES)) &
                (Order.is_prepared == 0) &
                (Order.status == 'Pending')
            )
            .order_by(Order.id.asc())
            .limit(5)
        )

        if not candidates:
            return None

        # Try to atomically claim one of the candidates
        for candidate in candidates:
            updated = Order.update(
                is_prepared=1,
                updated_at=tehran_now()
            ).where(
                (Order.id == candidate.id) &
                (Order.is_prepared == 0)
            ).execute()

            if updated > 0:
                return Order.get_by_id(candidate.id)

        # All candidates were claimed by other threads
        return None

    def _process_order(self):
        """
        Process a single order through the preparation pipeline.

        Routes to appropriate handler based on service_type, then:
        1. Handler navigates to target and captures data
        2. Handler performs first action via browser
        3. We save action_data and create OrderAction records

        Error handling:
        - TimeoutError: Temporary issue, reset for retry
        - RetryableError: Temporary issue, reset for retry
        - Other Exception: Permanent issue (bad link, private account), cancel order
        """
        try:
            # Route to appropriate handler based on service type
            if self.order.service_type == 'view_story':
                from .handlers.StoryPrepareHandler import StoryPrepareHandler
                handler = StoryPrepareHandler(self.ig, self)
                handler.prepare(self.order)

            elif self.order.service_type == 'save_post':
                from .handlers.SavePostPrepareHandler import SavePostPrepareHandler
                handler = SavePostPrepareHandler(self.ig, self)
                handler.prepare(self.order)

            elif self.order.service_type == 'comment':
                from .handlers.CommentPrepareHandler import CommentPrepareHandler
                handler = CommentPrepareHandler(self.ig, self)
                handler.prepare(self.order)

            else:
                raise Exception(f'Unknown service_type: {self.order.service_type}')

            # Validate that handler captured the required data
            if not self.captured_data:
                raise Exception('Failed to capture data')

            # Save captured data to order for API execution phase
            self._save_action_data()

            # Create or update OrderAction records
            # For comments: actions already exist (created by Laravel with content)
            # For others: we need to create them here
            if self.order.service_type == 'comment':
                self._mark_first_comment_action_sent()
            else:
                self._create_order_actions()

            self.ig.account.add_cli(f'Order #{self.order.id} prepared successfully')

        except TimeoutError as e:
            # Timeout is usually temporary - reset for retry
            self._handle_timeout(str(e))

        except RetryableError as e:
            # Explicit retryable error - reset for retry
            self._handle_timeout(str(e))
            self._log_to_file(f'RETRYABLE: {str(e)}', 'retry')

        except Exception as e:
            # Other errors are usually client's fault - cancel and charge
            self._handle_error(str(e))
            self._log_to_file(f'EXCEPTION: {str(e)}\n{traceback.format_exc()}', 'exception')

        finally:
            # Always clean up listeners and exit current view
            self._cleanup_listeners()
            self._force_exit()

    def _save_action_data(self):
        """
        Save captured GraphQL data to order and mark as fully prepared.

        action_data contains everything needed for API execution:
        - doc_id: GraphQL document ID
        - media_id: For posts/comments
        - reelId, reelMediaId, etc: For stories

        is_prepared=2 means order is ready for API execution phase.
        """
        Order.update(
            is_prepared=2,
            action_data=self.captured_data,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _create_order_actions(self):
        """
        Create OrderAction records for view_story and save_post orders.

        This method handles two scenarios:

        1. Fresh order (first time preparing):
           - Create one action with status='sent' (preparer just did this action)
           - Create remaining actions with status='free' (for API execution)
           - Set completed_count=1
           - Deduct balance for 1 action

        2. Re-prepare (order came back from execution phase after retries failed):
           - Actions already exist from first prepare
           - Just mark one more action as 'sent' (preparer did it again)
           - Increment completed_count by 1 (not set to 1!)
           - Deduct balance for 1 action

        This distinction is critical for correct balance deduction and count tracking.
        """
        # Try to find a free action directly (avoids a separate COUNT query)
        # If one exists, this is a re-prepare scenario
        free_action = (
            OrderAction
            .select()
            .where(
                (OrderAction.order == self.order.id) &
                (OrderAction.status == 'free')
            )
            .order_by(OrderAction.id.asc())
            .first()
        )

        if free_action:
            # Re-prepare scenario: free action exists, mark it as sent
            self.ig.account.add_cli(f'Re-prepare: marking one free action as sent')

            # Mark this action as sent by preparer
            updated = OrderAction.update(
                status='sent',
                account=self.ig.account,
                updated_at=tehran_now()
            ).where(
                (OrderAction.id == free_action.id) &
                (OrderAction.status == 'free')
            ).execute()

            if updated > 0:
                # Increment completed_count (not set to 1!)
                Order.update(
                    completed_count=Order.completed_count + 1
                ).where(
                    Order.id == self.order.id
                ).execute()

                # Deduct balance for this one action
                Balance.deduct_for_actions(self.order.service_type, 1)

                # Check if order is now complete
                self._check_order_completion()

                self.ig.account.add_cli(f'Marked one existing action as sent, incremented completed_count')

            return

        # No free action found - check if any actions exist at all
        has_any = (
            OrderAction
            .select()
            .where(OrderAction.order == self.order.id)
            .exists()
        )

        if has_any:
            # Re-prepare but all actions are sent/processing - nothing to do
            self.ig.account.add_cli(f'No free actions left for re-prepare')
            return

        # Fresh order: create all actions from scratch

        # First action - preparer's action (already done via browser)
        OrderAction.create(
            order_id=self.order.id,
            type=self.order.service_type,
            status='sent',
            account=self.ig.account
        )

        # Set completed_count to 1 (fresh start)
        Order.update(
            completed_count=1
        ).where(
            Order.id == self.order.id
        ).execute()

        # Deduct balance for this one action
        Balance.deduct_for_actions(self.order.service_type, 1)

        # Create remaining actions with free status
        remaining_count = self.order.total_count - 1

        if remaining_count > 0:
            actions = [
                {'order_id': self.order.id, 'type': self.order.service_type, 'status': 'free'}
                for _ in range(remaining_count)
            ]
            OrderAction.insert_many(actions).execute()

        # Check if single-action order is already complete
        self._check_order_completion()

        self.ig.account.add_cli(f'Created 1 sent + {remaining_count} free actions')

    def _mark_first_comment_action_sent(self):
        """
        Mark the first comment action as sent (for comment orders).

        For comments, OrderAction records are created by Laravel (OrderController)
        with the comment content already set. The preparer just needs to:
        1. Find the first free action
        2. Mark it as sent (preparer posted this comment via browser)
        3. Increment completed_count
        4. Deduct balance

        Uses completed_count + 1 (not =1) to handle re-prepare scenario correctly.
        """
        # Find first free action to mark as sent
        first_action = (
            OrderAction
            .select()
            .where(
                (OrderAction.order == self.order.id) &
                (OrderAction.status == 'free')
            )
            .order_by(OrderAction.id.asc())
            .first()
        )

        if first_action:
            # Atomically mark as sent (check status to prevent double-marking)
            updated = OrderAction.update(
                status='sent',
                account=self.ig.account,
                updated_at=tehran_now()
            ).where(
                (OrderAction.id == first_action.id) &
                (OrderAction.status == 'free')
            ).execute()

            if updated > 0:
                # Increment completed_count (handles both fresh and re-prepare)
                Order.update(
                    completed_count=Order.completed_count + 1
                ).where(
                    Order.id == self.order.id
                ).execute()

                # Deduct balance for this one action
                Balance.deduct_for_actions('comment', 1)

                # Check if order is now complete
                self._check_order_completion()

                self.ig.account.add_cli(f'Marked first comment action as sent')
        else:
            # No free actions - might be re-prepare with all actions already sent
            self.ig.account.add_cli(f'No free comment actions to mark as sent')

    def _handle_timeout(self, message):
        """
        Handle timeout or retryable error - reset order for retry.

        Timeouts are usually temporary issues (slow network, Instagram lag).
        Reset is_prepared to 0 so another thread can try again.
        Don't cancel or charge - this isn't the client's fault.
        """
        self.ig.account.add_cli(f'Order #{self.order.id} timeout: {message}')

        Order.update(
            is_prepared=0,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

    def _handle_error(self, message):
        """
        Handle permanent error - cancel order and charge remaining amount.

        Permanent errors are usually the client's fault:
        - Invalid link (bad URL, typo)
        - Private account
        - Deleted post/story
        - Comments disabled

        We cancel the order and charge for remaining actions.
        If some actions were already completed, we only charge for the rest.
        """
        self.ig.account.add_cli(f'Order #{self.order.id} failed: {message}')

        # Cancel the order
        Order.update(
            status='Canceled',
            is_prepared=0,
            description=message,
            updated_at=tehran_now()
        ).where(
            Order.id == self.order.id
        ).execute()

        # Charge for remaining actions
        self._charge_remaining()

    def _charge_remaining(self):
        """
        Deduct balance for remaining (uncompleted) actions.

        Formula: remaining = total_count - completed_count

        This handles both:
        - Fresh orders: completed_count=0, charges full amount
        - Re-prepare orders: completed_count>0, charges only remaining
        """
        # Get fresh data to ensure accurate count
        fresh_order = (
            Order
            .select(Order.total_count, Order.completed_count)
            .where(Order.id == self.order.id)
            .first()
        )

        if fresh_order:
            remaining = fresh_order.total_count - fresh_order.completed_count

            if remaining > 0:
                total_charge = Balance.deduct_for_actions(self.order.service_type, remaining)
                self.ig.account.add_cli(f'Charged ${total_charge} for {remaining} remaining actions')
            else:
                self.ig.account.add_cli(f'No remaining actions to charge')

    def _check_order_completion(self):
        """
        Check if order has reached completion threshold and mark as Completed.

        This is called after incrementing completed_count to handle the case
        where the last action was completed during prepare phase (re-prepare scenario).

        Uses atomic UPDATE with conditions to prevent race conditions.
        """
        updated = Order.update(
            status='Completed'
        ).where(
            (Order.id == self.order.id) &
            (Order.completed_count >= Order.total_count) &
            (Order.status != 'Completed')
        ).execute()

        if updated > 0:
            self.ig.account.add_cli(f'Order #{self.order.id} marked as Completed')

    def _cleanup_listeners(self):
        """
        Remove all registered network event listeners.

        Listeners capture GraphQL responses during navigation.
        Must be cleaned up to prevent memory leaks and duplicate captures.
        """
        for listener in self.listeners:
            try:
                self.ig.page.remove_listener('response', listener)
            except:
                pass
        self.listeners = []

    def _force_exit(self):
        """
        Exit current view (story viewer or post modal).

        Press Escape to close any open overlay before moving to next order.
        """
        try:
            self.ig.page.keyboard.press('Escape')
            self.ig.pause(300, 500)
        except:
            pass

    def _log_to_file(self, message, log_type='info'):
        """
        Log message to file for debugging and analysis.

        Separate log file for order preparation helps track issues
        specific to the prepare phase.
        """
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
        """
        Wait for GraphQL data to be captured by network listener.

        The handler sets up a network listener that captures specific
        GraphQL responses. This method waits until data is captured
        or timeout is reached.

        Args:
            timeout: Maximum seconds to wait

        Raises:
            TimeoutError: If data not captured within timeout
        """
        start = time.time()

        while time.time() - start < timeout:
            if self.captured_data:
                return True
            time.sleep(1)

        raise TimeoutError('Timeout waiting for data capture')