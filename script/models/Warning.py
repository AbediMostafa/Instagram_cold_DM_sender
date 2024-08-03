from datetime import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account


class Warning(BaseModel):
    cause = TextField(null=True)
    duration = IntegerField(default=24)
    account = ForeignKeyField(Account, backref='warnings', null=True)

    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        table_name = 'warnings'
