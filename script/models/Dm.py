from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account
from .Lead import Lead


class Dm(BaseWithTimeZoneModel):
    account = ForeignKeyField(Account, backref='dms', null=True)
    lead = ForeignKeyField(Lead, backref='dms', null=True)
    text = TextField()
    times = IntegerField()


    class Meta:
        table_name = 'dms'
