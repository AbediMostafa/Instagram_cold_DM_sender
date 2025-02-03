from peewee import *
from .Account import Account
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Log(BaseWithTimeZoneModel):
    log = TextField(null=True)
    account = ForeignKeyField(Account, backref='logs')

    class Meta:
        table_name = 'logs'
