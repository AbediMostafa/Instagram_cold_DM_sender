from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Service(BaseWithTimeZoneModel):
    service = CharField()
    title = CharField()
    description = TextField()

    static_services = ['account_profiler', 'reels_spammer']
    active_statuses = ['Pending', 'In progress']
    class Meta:
        table_name = 'services'

    def has_active_orders(self) -> bool:
        from .Order import Order  # lazy import to avoid circular import

        return (
            Order
            .select()
            .where(
                (Order.service == self) &
                (Order.status.in_(self.active_statuses))
            )
            .exists()
        )

    def should_run(self) -> bool:
        return (
                self.service in self.static_services
                or self.has_active_orders()
        )