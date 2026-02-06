from peewee import *
from .Proxy import Proxy
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Profile(BaseWithTimeZoneModel):
    title = CharField(null=True)
    profile_id = CharField()
    folder = CharField(null=True)
    is_used = SmallIntegerField(default=0)
    proxy = ForeignKeyField(Proxy, backref='profiles', null=True)

    class Meta:
        table_name = 'profiles'


def get_next():
    query = Profile.select().where(Profile.is_used == 0)

    if not query.exists():
        Profile.update(is_used=False).execute()

    next_profile = (query
                    .order_by(Profile.id)
                    .first())

    if next_profile:
        next_profile.is_used = True
        next_profile.save()
        print(f'Selected profile : {next_profile.id}')

    return next_profile
