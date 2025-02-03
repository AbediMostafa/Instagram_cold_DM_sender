import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now


class Category(BaseWithTimeZoneModel):
    title = CharField()
    description = TextField(null=True)

    updated_at = DateTimeField(null=True, default=tehran_now)

    class Meta:
        table_name = 'categories'
