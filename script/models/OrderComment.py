import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now
from .Order import Order
from .Account import Account


class OrderComment(BaseWithTimeZoneModel):
    order = ForeignKeyField(Order, backref='order_comments')
    content = TextField()
    account = ForeignKeyField(Account, backref='order_comments')
    status = CharField(default='free')
    updated_at = DateTimeField(null=True)

    def set_status_to(self, status):
        self.status = status
        self.updated_at = tehran_now()
        self.save()

    class Meta:
        table_name = 'order_comments'


def get_next_comment_for_order(order):
    db = OrderComment._meta.database

    with db.atomic() as txn:
        comment = (
            OrderComment
            .select()
            .where(
                (OrderComment.order == order) &
                (OrderComment.status == 'free')
            )
            .order_by(OrderComment.id)
            .for_update()
            .first()
        )

        if not comment:
            return None

        updated = (
            OrderComment
            .update(
                status='processing',
                updated_at=tehran_now()
            )

            .where(
                (OrderComment.id == comment.id) &
                (OrderComment.status == 'free')
            )
            .execute()
        )

        if updated == 0:
            txn.rollback()
            return None

        return comment


def release_stuck_comments():
    from datetime import timedelta

    """
    If a comment is in 'processing' state for more than 6 minutes,
    set it back to 'free'
    """
    five_minutes_ago = tehran_now() - timedelta(minutes=6)

    updated_count = (
        OrderComment.update(
            status='free'
        )
        .where(
            (OrderComment.status == 'processing') &
            (OrderComment.updated_at.is_null(False)) &
            (OrderComment.updated_at < five_minutes_ago)
        )
        .execute()
    )

    return updated_count
