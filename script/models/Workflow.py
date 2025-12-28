import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Service import Service


class Workflow(BaseWithTimeZoneModel):
    title = CharField()

    service = ForeignKeyField(
        Service,
        backref='workflows',
        null=True,
        on_delete='SET NULL'
    )

    class Meta:
        table_name = 'workflows'