from peewee import *
from .Base import BaseModel
from .Proxy import Proxy
from datetime import datetime, timedelta


class Profile(BaseModel):
    title = CharField()
    profile_id = CharField()
    folder = CharField()
    is_used = SmallIntegerField(default=0)

    proxy = ForeignKeyField(Proxy, backref='profiles', null=True)

    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        table_name = 'profiles'
