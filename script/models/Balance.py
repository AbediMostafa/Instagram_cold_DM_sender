from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Balance(BaseWithTimeZoneModel):
    customer = CharField()
    balance = DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        table_name = 'balances'
