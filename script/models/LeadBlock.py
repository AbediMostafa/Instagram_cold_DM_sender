from peewee import *
from .Account import Account
from .Base import BaseModel


class LeadBlock(BaseModel):
    account = ForeignKeyField(Account, backref='lead_block', null=True)
    blocked = SmallIntegerField(default=0)

    class Meta:
        table_name = 'lead_blocks'

