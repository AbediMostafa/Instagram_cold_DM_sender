import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account


class Cli(BaseModel):
    log = TextField(null=True)
    account = ForeignKeyField(Account, backref='clis')
    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'clis'
