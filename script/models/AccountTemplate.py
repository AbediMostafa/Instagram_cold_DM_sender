from peewee import *
from playhouse.postgres_ext import BinaryJSONField
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account
from .Template import Template


class AccountTemplate(BaseWithTimeZoneModel):
    """
    Pivot model linking accounts to the templates they have posted.
    created_at is inherited from BaseWithTimeZoneModel and acts as both
    the assignment time (for pending rows) and the post time (the worker
    overwrites it with the real post timestamp on completion).
    """
    account = ForeignKeyField(Account, backref='templates')
    template = ForeignKeyField(Template, backref='account_template')

    status = CharField(default='pending')
    url = CharField(null=True)

    like_count = IntegerField(default=0)
    comment_count = IntegerField(default=0)
    view_count = IntegerField(default=0)
    save_count = IntegerField(default=0)
    repost_count = IntegerField(default=0)

    stats = BinaryJSONField(null=True)

    updated_at = DateTimeField(null=True)

    statuses = [
        'pending',
        'processing',
        'completed',
    ]

    class Meta:
        table_name = 'account_template'