import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now
from .OrderComment import OrderComment
from .Order import Order
from .Account import Account


class CommentLog(BaseWithTimeZoneModel):
    order = ForeignKeyField(Order, backref='comment_logs', on_delete='CASCADE')
    comment = ForeignKeyField(OrderComment, backref='comment_logs', on_delete='CASCADE')
    account = ForeignKeyField(Account, backref='comment_logs')
    status = CharField(default='pending')
    updated_at = DateTimeField(null=True, default=tehran_now)

    class Meta:
        table_name = 'comment_logs'
