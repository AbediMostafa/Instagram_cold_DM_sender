from peewee import *
from .Base import BaseModel
from .Command import Command
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Url(BaseWithTimeZoneModel):
    command = ForeignKeyField(Command, backref='urls', on_delete='CASCADE')
    url = CharField()

    class Meta:
        table_name = 'urls'