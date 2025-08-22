from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Category import Category
from peewee import *


class DmPost(BaseWithTimeZoneModel):
    title = CharField()
    media_id = CharField()
    category = ForeignKeyField(Category, backref='lead_sources', null=True)
    description = TextField(null=True)
    priority = SmallIntegerField(default=0)

    class Meta:
        table_name = 'dm_posts'


def get_dm_post_for_lead(priority):
    return (
        DmPost.select()
        .where(DmPost.priority == priority)
        .first()
    )
