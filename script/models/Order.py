import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Service import Service
from script.extra.helper import tehran_now


class Order(BaseWithTimeZoneModel):
    customer = CharField()
    service_type = CharField()
    target_link = TextField()
    total_count = IntegerField()
    completed_count = IntegerField(default=0)
    status = CharField(default='Pending')
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
    from .OrderAction import OrderAction

    # Orders not completed
    order = (
        Order
        .select()
        .where(Order.completed_count < Order.total_count)
        .where(Order.status.in_(['Pending', 'In progress']))
        # .where(Order.service_type == service_type)
        .where(
            # This account has NOT sent any comment for this order
            ~Order.id.in_(
                OrderAction
                .select(OrderAction.order)
                .where(OrderAction.account == account)
            )
        )
        .order_by(Order.id)
    ).first()

    order.completed_count = order.completed_count + 1
    order.save()

    return order
