from peewee import *
from .Account import Account
from .Base import BaseModel


class AccountSpec(BaseModel):
    account = ForeignKeyField(Account, backref='specs', unique=True, on_delete='CASCADE')

    reels_count = IntegerField(default=0)
    avg_reel_views = BigIntegerField(default=0)
    min_reel_views = BigIntegerField(default=0)
    max_reel_views = BigIntegerField(default=0)
    total_reel_views = BigIntegerField(default=0)

    last_reels_scan_at = DateTimeField(null=True)

    class Meta:
        table_name = 'account_specs'
