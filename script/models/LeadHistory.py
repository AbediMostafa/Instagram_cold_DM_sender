from peewee import *
from .Lead import Lead
from .User import User
from .Account import Account
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class LeadHistory(BaseWithTimeZoneModel):
    state = CharField()
    times = IntegerField(null=True)
    lead = ForeignKeyField(Lead, backref='leadHistories')
    account = ForeignKeyField(User, backref='leadHistories', null=True)
    user = ForeignKeyField(Account, backref='leadHistories', null=True)

    class Meta:
        table_name = 'lead_histories'
