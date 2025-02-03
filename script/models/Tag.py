from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Tag(BaseWithTimeZoneModel):
    title = CharField()

    class Meta:
        table_name = 'tags'
