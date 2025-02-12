from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Category import Category
from peewee import *


class Hashtag(BaseWithTimeZoneModel):
    title = CharField()
    is_used = SmallIntegerField(default=0)
    category = ForeignKeyField(Category, backref='hashtags', null=True)

    class Meta:
        table_name = 'hashtags'


def free_hashtags_query(count, category=None):
    query = Hashtag.select().where(Hashtag.is_used == 0)

    if category:
        query = query.where(Hashtag.category == category)

    return query.order_by(Hashtag.id).limit(count)


def get_hashtag(count, category=None):
    query = free_hashtags_query(count, category)

    # Refresh hashtags if no free hashtags exist
    if not query.exists():
        Hashtag.update(is_used=False).execute()

    hashtags = query

    if hashtags.count():
        for hashtag in hashtags:
            hashtag.is_used = True
            hashtag.save()

    return hashtags
