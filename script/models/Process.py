import datetime
from peewee import *
from .Account import Account
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Process(BaseWithTimeZoneModel):
    pid = BigIntegerField()
    status = CharField(default='running')

    class Meta:
        table_name = 'processes'
