from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Service(BaseWithTimeZoneModel):
    service = CharField()
    title = CharField()
    description = TextField()

    class Meta:
        table_name = 'services'