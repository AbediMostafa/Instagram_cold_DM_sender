import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Service import Service
from playhouse.postgres_ext import JSONField
from script.extra.helper import tehran_now


class Order(BaseWithTimeZoneModel):
    customer = CharField()
    service_type = CharField()
    target_link = TextField()
    total_count = IntegerField()
    completed_count = IntegerField(default=0)
    status = CharField(default='Pending')
    is_prepared  = IntegerField(default=0)
    action_data  = JSONField()
    description = TextField(null=True)
    updated_at = DateTimeField(null=True, default=tehran_now)

    service = ForeignKeyField(
        Service,
        backref='orders',
        null=True,
        on_delete='SET NULL'
    )

    def set_status_to(self, status):
        """Atomic status update"""
        Order.update(
            status=status,
            updated_at=tehran_now()
        ).where(
            Order.id == self.id
        ).execute()
        self.status = status

    def status_is(self, status):
        return self.status == status

    def fail(self, message):
        """Atomic fail"""
        Order.update(
            status='Canceled',
            description=message,
            updated_at=tehran_now()
        ).where(
            Order.id == self.id
        ).execute()

        self.status = 'Canceled'
        self.description = message

    def make_order_completed(self):
        """
        Atomically increment completed_count and mark as Completed if threshold is reached.
        Each UPDATE is atomic on its own - no transaction wrapper needed.
        """
        # Increment completed_count
        Order.update(
            completed_count=Order.completed_count + 1
        ).where(
            Order.id == self.id
        ).execute()

        # Mark as Completed if threshold reached
        Order.update(
            status='Completed'
        ).where(
            (Order.id == self.id) &
            (Order.completed_count >= Order.total_count) &
            (Order.status != 'Completed')
        ).execute()

    def actions(self):
        from .OrderAction import OrderAction

        """Get all actions for this order."""
        return OrderAction.select().where(OrderAction.order == self.id)

    def comments(self):
        """Get all comments for this order."""
        from .OrderComment import OrderComment
        return OrderComment.select().where(OrderComment.order == self.id)

    class Meta:
        table_name = 'orders'


def get_next_order_for_account(account):
    """
    Get the next available order for the given account using atomic UPDATE.

    Finds orders that:
    - Are not yet completed (completed_count < total_count)
    - Are in active status (Pending or In progress)
    - Have not been worked on by this account before

    Uses atomic UPDATE to safely increment completed_count and prevent
    race conditions between concurrent threads.

    Args:
        account: Account model instance

    Returns:
        Order instance or None if no order available
    """
    from .OrderAction import OrderAction

    # Get multiple candidates to handle race conditions
    candidates = list(
        Order
        .select(Order.id)
        .where(Order.completed_count < Order.total_count)
        .where(Order.status.in_(['Pending', 'In progress']))
        .where(
            # This account has NOT worked on this order before
            ~Order.id.in_(
                OrderAction
                .select(OrderAction.order)
                .where(OrderAction.account == account)
            )
        )
        .order_by(Order.id)
        .limit(5)
    )

    if not candidates:
        return None

    # Try to atomically claim one of the candidates
    for candidate in candidates:
        updated = (
            Order
            .update(completed_count=Order.completed_count + 1)
            .where(
                (Order.id == candidate.id) &
                (Order.completed_count < Order.total_count)
            )
            .execute()
        )

        if updated > 0:
            return Order.get_by_id(candidate.id)

    return None