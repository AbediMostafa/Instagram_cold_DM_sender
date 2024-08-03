import datetime

from peewee import *
from .Base import BaseModel
from .Lead import Lead
from .User import User
from .Account import Account


class LeadHistory(BaseModel):
    state = CharField()
    times = IntegerField(null=True)
    lead = ForeignKeyField(Lead, backref='leadHistories')
    account = ForeignKeyField(User, backref='leadHistories', null=True)
    user = ForeignKeyField(Account, backref='leadHistories', null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'lead_histories'
