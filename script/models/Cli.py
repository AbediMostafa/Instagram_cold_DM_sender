import datetime
from peewee import *
from .Account import Account
from .Process import Process
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Cli(BaseWithTimeZoneModel):
    log = TextField(null=True)
    account = ForeignKeyField(Account, backref='clis')
    process = ForeignKeyField(Process, backref='processes')

    class Meta:
        table_name = 'clis'
