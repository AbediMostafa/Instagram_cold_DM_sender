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
        self.status = status
        self.save()

    def status_is(self, status):
        return self.status == status

    def fail(self, message):
        self.status = 'Canceled'
        self.description = message
        self.save()

    def make_order_completed(self):
        """Check if all actions are done (sent/failed) and mark order as Completed"""
        from .OrderAction import OrderAction

        done_count = (
            OrderAction
            .select()
            .where(
                (OrderAction.order == self.id) &
                (OrderAction.status.in_(['sent', 'failed']))
            )
            .count()
        )

        print(f'Done: {done_count} / Total: {self.total_count}')

        if done_count >= self.total_count:
            (
                Order
                .update(status='Completed')
                .where(
                    (Order.id == self.id) &
                    (Order.status != 'Completed')
                )
                .execute()
            )

    def actions(self):
        """Get all actions for this order"""
        from .OrderAction import OrderAction
        return OrderAction.select().where(OrderAction.order == self.id)

    def comments(self):
        """Get all comments for this order (legacy support)"""
        from .OrderComment import OrderComment
        return OrderComment.select().where(OrderComment.order == self.id)

    class Meta:
        table_name = 'orders'