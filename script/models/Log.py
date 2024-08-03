import datetime

from peewee import *
from .Base import BaseModel
from .Account import Account


class Log(BaseModel):
    log = TextField(null=True)
    account = ForeignKeyField(Account, backref='logs')
    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'logs'
