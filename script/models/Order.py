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
    status = CharField(default='pending')
    description = TextField(null=True)
    updated_at = DateTimeField(null=True, default=tehran_now)

    service = ForeignKeyField(
        Service,
        backref='orders',
        null=True,
        on_delete='SET NULL'
    )

    def add_completed_count(self):
        (
            Order
            .update(completed_count=Order.completed_count + 1)
            .where(Order.id == self.id)
        ).execute()

        # Refresh object from DB
        self.refresh()

    def set_status_to(self, status):
        self.status = status
        self.save()

    def status_is(self, status):
        return self.status == status

    def fail(self, message):
        self.status = 'Canceled'
        self.description = message
        self.save()

    def refresh(self):
        fresh = Order.get(Order.id == self.id)
        self.completed_count = fresh.completed_count
        self.status = fresh.status

    def make_order_completed(self):
        print(f'Completed {self.completed_count}')
        print(f'total_count {self.total_count}')
        print(f'Aya completed ?{self.completed_count == self.total_count}')

        if self.completed_count == self.total_count:
            self.status = 'Completed'
            self.save()

        # Balance deduction moved to deduct_balance() in OrderAction.py
        # Called per action in mark_action_sent()

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