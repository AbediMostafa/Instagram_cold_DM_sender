from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now
from .Order import Order
from .Account import Account
from .Balance import Balance
from datetime import timedelta
from decimal import Decimal


# Rate per action type (divided by 1000)
ACTION_RATES = {
    'comment': Decimal('0.00025'),           # $0.25 / 1000
    'view_story': Decimal('0.000025'),       # $0.025 / 1000
    'view_all_stories': Decimal('0.00005'),  # $0.05 / 1000
    'save_post': Decimal('0.000025'),        # $0.025 / 1000
}


class OrderAction(BaseWithTimeZoneModel):
    """
    Model for tracking individual action items within an order.
    Each order can have multiple actions (e.g., 100 story views = 100 action records).
    """

    VALID_TYPES = [
        'comment',
        'view_story',
        'view_all_stories',
        'save_post',
    ]

    VALID_STATUSES = [
        'free',
        'processing',
        'sent',
        'failed',
    ]

    order = ForeignKeyField(Order, backref='order_actions')
    account = ForeignKeyField(Account, backref='order_actions', null=True)
    content = TextField(null=True)
    type = CharField(max_length=50)
    status = CharField(max_length=20, default='free')
    updated_at = DateTimeField(null=True)

    class Meta:
        table_name = 'order_actions'

    def set_status_to(self, status):
        self.status = status
        self.updated_at = tehran_now()
        self.save()

    def mark_as_processing(self, account):
        self.status = 'processing'
        self.account = account
        self.updated_at = tehran_now()
        self.save()

    def mark_as_sent(self):
        self.status = 'sent'
        self.updated_at = tehran_now()
        self.save()

    def reset_to_free(self):
        self.status = 'free'
        self.account = None
        self.updated_at = tehran_now()
        self.save()

    @classmethod
    def is_valid_type(cls, action_type):
        return action_type in cls.VALID_TYPES

    @classmethod
    def is_valid_status(cls, status):
        return status in cls.VALID_STATUSES


def get_next_action_for_account(account, action_types):
    """
    Get next available order action for the given account and action types.
    Uses FOR UPDATE to prevent race conditions with multiple threads.

    Args:
        account: Account model instance
        action_types: list of action type strings, e.g. ['view_story', 'view_all_stories']

    Returns:
        OrderAction or None
    """
    db = OrderAction._meta.database

    with db.atomic() as txn:
        action = (
            OrderAction
            .select()
            .join(Order)
            .where(
                (OrderAction.type.in_(action_types)) &
                (Order.status.in_(['Pending', 'In progress'])) &
                (OrderAction.status == 'free') &
                ~OrderAction.order.in_(
                    OrderAction
                    .select(OrderAction.order)
                    .where(OrderAction.account == account)
                )
            )
            .order_by(OrderAction.id)
            .for_update()
            .first()
        )

        if not action:
            return None

        updated = (
            OrderAction
            .update(
                status='processing',
                account=account,
                updated_at=tehran_now()
            )
            .where(
                (OrderAction.id == action.id) &
                (OrderAction.status == 'free')
            )
            .execute()
        )

        if updated == 0:
            txn.rollback()
            return None

        if action.order.status == 'Pending':
            action.order.set_status_to('In progress')

        return OrderAction.get_by_id(action.id)


def get_batch_actions_for_account(account, action_types, batch_size=1):
    """
    Get multiple actions from DIFFERENT orders for the given account.
    Each action will be from a unique order (no two actions from same order).

    Args:
        account: Account model instance
        action_types: list of action type strings
        batch_size: number of actions to get (from different orders)

    Returns:
        list of OrderAction instances
    """
    db = OrderAction._meta.database
    actions = []
    locked_order_ids = []

    with db.atomic():
        for _ in range(batch_size):
            # Build exclusion list: orders this account already worked on + orders we just locked
            excluded_orders = (
                OrderAction
                .select(OrderAction.order)
                .where(OrderAction.account == account)
            )

            action = (
                OrderAction
                .select()
                .join(Order)
                .where(
                    (OrderAction.type.in_(action_types)) &
                    (Order.status.in_(['Pending', 'In progress'])) &
                    (OrderAction.status == 'free') &
                    ~OrderAction.order.in_(excluded_orders) &
                    ~OrderAction.order.in_(locked_order_ids)  # Exclude orders we already picked
                )
                .order_by(OrderAction.id)
                .for_update()
                .first()
            )

            if not action:
                break

            updated = (
                OrderAction
                .update(
                    status='processing',
                    account=account,
                    updated_at=tehran_now()
                )
                .where(
                    (OrderAction.id == action.id) &
                    (OrderAction.status == 'free')
                )
                .execute()
            )

            if updated == 0:
                continue

            if action.order.status == 'Pending':
                action.order.set_status_to('In progress')

            locked_order_ids.append(action.order_id)
            actions.append(OrderAction.get_by_id(action.id))

    return actions


def release_stuck_actions(minutes=6):
    """
    Reset actions that have been in 'processing' state for too long.
    This handles cases where a worker crashed mid-execution.

    Args:
        minutes: Number of minutes after which to consider an action stuck

    Returns:
        Number of actions reset
    """
    threshold = tehran_now() - timedelta(minutes=minutes)

    updated_count = (
        OrderAction
        .update(
            status='free',
            account=None
        )
        .where(
            (OrderAction.status == 'processing') &
            (OrderAction.updated_at.is_null(False)) &
            (OrderAction.updated_at < threshold)
        )
        .execute()
    )

    return updated_count


def deduct_balance(action_type):
    """
    Deduct balance for the customer based on action type.
    Currently hardcoded for 'sadeghi' customer.

    Args:
        action_type: Type of action (view_story, view_all_stories, save_post, comment)

    Returns:
        True if successful, False otherwise
    """
    rate = ACTION_RATES.get(action_type, Decimal('0.000025'))

    try:
        balance = Balance.get(Balance.customer == 'sadeghi')
        balance.balance = balance.balance - rate
        balance.save()
        return True
    except Balance.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error deducting balance: {e}")
        return False


def mark_action_completed(action):
    """
    Mark an action as sent and check if order is completed.
    Note: deduct_balance() is called separately in each module's mark_action_sent()

    Args:
        action: OrderAction model instance
    """
    action.mark_as_sent()
    action.order.make_order_completed()


def mark_action_failed(action):
    """
    Mark an action as failed (client error - private account, bad link, etc.)
    Note: deduct_balance() should still be called - client pays for their mistakes.

    Args:
        action: OrderAction model instance
    """
    action.status = 'failed'
    action.updated_at = tehran_now()
    action.save()

    action.order.make_order_completed()


def get_order_actions_stats(order_id):
    """
    Get statistics for an order's actions.

    Returns:
        dict with counts for each status
    """
    from peewee import fn

    stats = (
        OrderAction
        .select(OrderAction.status, fn.COUNT(OrderAction.id).alias('count'))
        .where(OrderAction.order == order_id)
        .group_by(OrderAction.status)
        .dicts()
    )

    result = {'free': 0, 'processing': 0, 'sent': 0, 'failed': 0}
    for stat in stats:
        result[stat['status']] = stat['count']

    return result