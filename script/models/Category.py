import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now


class Category(BaseWithTimeZoneModel):
    title = CharField()
    description = TextField(null=True)
    number_of_follow_ups = IntegerField(default=0)
    hour_interval = IntegerField(default=24)  # New field added
    updated_at = DateTimeField(null=True, default=tehran_now)

    class Meta:
        table_name = 'categories'
