from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Proxy import Proxy  # assuming you have this model


class Ip(BaseWithTimeZoneModel):
    ip = CharField()
    type = CharField()

    proxy = ForeignKeyField(
        Proxy,
        backref='ips',
        null=True,
        on_delete='SET NULL'
    )

    class Meta:
        table_name = 'ips'