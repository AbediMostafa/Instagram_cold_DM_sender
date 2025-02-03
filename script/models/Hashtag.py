from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from peewee import *


class Hashtag(BaseWithTimeZoneModel):
    title = CharField()
    is_used = SmallIntegerField(default=0)

    class Meta:
        table_name = 'hashtags'


def free_hashtags_query(count):
    hashtags = (
        Hashtag.select()
        .where(Hashtag.is_used == 0)
        .order_by(Hashtag.id)
        .limit(count)
    )

    return hashtags


def get_hashtag(count):
    query = free_hashtags_query(count)

    # Refresh hashtags if no free hashtags exist
    if not query.exists():
        Hashtag.update(is_used=False).execute()

    hashtags = query

    if hashtags.count():
        for hashtag in hashtags:
            print(hashtag.title)

            hashtag.is_used = True
            hashtag.save()

    return hashtags

