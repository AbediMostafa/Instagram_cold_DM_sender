from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account
from .Ip import Ip


class AccountIp(BaseWithTimeZoneModel):
    account = ForeignKeyField(
        Account,
        backref='account_ips',
        on_delete='CASCADE'
    )

    ip = ForeignKeyField(
        Ip,
        backref='account_ips',
        on_delete='CASCADE'
    )

    class Meta:
        table_name = 'account_ip'