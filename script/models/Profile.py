from peewee import *
from .Proxy import Proxy
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Profile(BaseWithTimeZoneModel):
    title = CharField()
    profile_id = CharField()
    folder = CharField()
    proxy = ForeignKeyField(Proxy, backref='profiles', null=True)

    class Meta:
        table_name = 'profiles'
