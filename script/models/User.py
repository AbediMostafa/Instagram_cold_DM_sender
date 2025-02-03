from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now


class User(BaseWithTimeZoneModel):
    name = CharField()
    email = CharField()
    password = CharField()

    updated_at = DateTimeField(null=True, default=tehran_now)

    class Meta:
        table_name = 'users'
