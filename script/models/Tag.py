from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Tag(BaseWithTimeZoneModel):
    title = CharField()

    class Meta:
        table_name = 'tags'


def get_or_create_tag(title):
    tag, _ = Tag.get_or_create(title=title)
    return tag
