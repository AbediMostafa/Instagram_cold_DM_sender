from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now
from .Order import Order
from .Account import Account
from .Balance import Balance
from datetime import timedelta
from decimal import Decimal
import random


# Rate per action type (divided by 1000)
ACTION_RATES = {
    'comment': Decimal('0.0003'),             # $0.30 / 1000
    'view_story': Decimal('0.00005'),         # $0.05 / 1000
    'view_all_stories': Decimal('0.00005'),   # $0.05 / 1000
    'save_post': Decimal('0.00004'),          # $0.04 / 1000
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
        """Reset action to free status - uses atomic UPDATE"""
        OrderAction.update(
            status='free',
            account=None,
            updated_at=tehran_now()
        ).where(
            OrderAction.id == self.id
        ).execute()

        self.status = 'free'
        self.account = None

    @classmethod
    def is_valid_type(cls, action_type):
        return action_type in cls.VALID_TYPES

    @classmethod
    def is_valid_status(cls, status):
        return status in cls.VALID_STATUSES


def get_single_action_for_account(account, action_types, excluded_order_ids=None):
    """
    Get a single action for the given account.
    Uses atomic UPDATE instead of FOR UPDATE to avoid deadlocks.

    Args:
        account: Account model instance
        action_types: list of action type strings
        excluded_order_ids: list of order IDs to exclude (orders already processed in this session)

    Returns:
        OrderAction or None
    """
    if excluded_order_ids is None:
        excluded_order_ids = []

    # Get orders this account already worked on
    worked_order_ids = list(
        OrderAction
        .select(OrderAction.order)
        .where(OrderAction.account == account)
        .distinct()
        .tuples()
    )
    worked_order_ids = [x[0] for x in worked_order_ids]

    # Combine with excluded orders
    all_excluded = set(worked_order_ids + excluded_order_ids)

    # Random offset to distribute load across threads
    random_offset = random.randint(0, 20)

    # Build query - prioritize older orders first
    query = (
        OrderAction
        .select(OrderAction.id, OrderAction.order)
        .join(Order)
        .where(
            (OrderAction.type.in_(action_types)) &
            (Order.status.in_(['Pending', 'In progress'])) &
            (OrderAction.status == 'free')
        )
        .order_by(Order.id, OrderAction.id)
        .offset(random_offset)
        .limit(10)
    )

    # Add exclusion if we have orders to exclude
    if all_excluded:
        query = query.where(~(OrderAction.order.in_(all_excluded)))

    candidates = list(query)

    if not candidates:
        return None

    # Try to claim one of the candidates
    for candidate in candidates:
        updated = (
            OrderAction
            .update(
                status='processing',
                account=account,
                updated_at=tehran_now()
            )
            .where(
                (OrderAction.id == candidate.id) &
                (OrderAction.status == 'free')
            )
            .execute()
        )

        if updated > 0:
            # Successfully claimed - update order status if needed
            Order.update(
                status='In progress'
            ).where(
                (Order.id == candidate.order_id) &
                (Order.status == 'Pending')
            ).execute()

            return OrderAction.get_by_id(candidate.id)

    return None


def deduct_balance(action_type):
    """
    Deduct balance atomically.
    """
    rate = ACTION_RATES.get(action_type, Decimal('0.000025'))

    try:
        updated = Balance.update(
            balance=Balance.balance - rate
        ).where(
            Balance.customer == 'sadeghi'
        ).execute()

        return updated > 0
    except Exception as e:
        print(f"Error deducting balance: {e}")
        return False


def mark_action_completed(action):
    """
    Mark action as sent and increment order completed_count atomically.
    Order: First increment count, then update action status.
    This ensures count is never less than actual sent actions.
    """
    # First increment completed_count
    Order.update(
        completed_count=Order.completed_count + 1
    ).where(
        Order.id == action.order_id
    ).execute()

    # Then mark action as sent
    OrderAction.update(
        status='sent',
        updated_at=tehran_now()
    ).where(
        OrderAction.id == action.id
    ).execute()

    # Mark order as Completed if threshold reached
    Order.update(
        status='Completed'
    ).where(
        (Order.id == action.order_id) &
        (Order.completed_count >= Order.total_count) &
        (Order.status != 'Completed')
    ).execute()


def mark_action_failed(action):
    """
    Mark action as failed and increment completed_count.
    Client pays for their mistakes.
    Order: First increment count, then update action status.
    """
    # First increment completed_count
    Order.update(
        completed_count=Order.completed_count + 1
    ).where(
        Order.id == action.order_id
    ).execute()

    # Then mark action as failed
    OrderAction.update(
        status='failed',
        updated_at=tehran_now()
    ).where(
        OrderAction.id == action.id
    ).execute()

    # Mark order as Completed if threshold reached
    Order.update(
        status='Completed'
    ).where(
        (Order.id == action.order_id) &
        (Order.completed_count >= Order.total_count) &
        (Order.status != 'Completed')
    ).execute()


def get_order_actions_stats(order_id):
    """
    Get statistics for an order's actions.
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