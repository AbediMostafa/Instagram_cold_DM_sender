from datetime import datetime

from peewee import *
from .Base import BaseModel
from .Account import Account
from .Lead import Lead


class Dm(BaseModel):
    account = ForeignKeyField(Account, backref='dms', null=True)
    lead = ForeignKeyField(Lead, backref='dms', null=True)
    text = TextField()
    times = IntegerField()

    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        table_name = 'dms'
