import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
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

    class Meta:
        table_name = 'orders'


def get_next_order_for_account(account, service_type ='comment'):
    from .OrderComment import OrderComment

    # Orders not completed
    query = (
        Order
        .select()
        .where(Order.completed_count < Order.total_count)
        .where(Order.status.in_(['Pending', 'In progress']))
        # .where(Order.service_type == service_type)
        .where(
            # This account has NOT sent any comment for this order
            ~Order.id.in_(
                OrderComment
                .select(OrderComment.order)
                .where(OrderComment.account == account)
            )
        )
        .order_by(Order.id)
    )

    return query.first()
