import datetime

from peewee import *
from .Base import BaseModel
from .Account import Account
from .Lead import Lead


class Thread(BaseModel):
    thread_id = CharField()
    account = ForeignKeyField(Account, backref='threads', null=True)
    lead = ForeignKeyField(Lead, backref='threads', null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'threads'
