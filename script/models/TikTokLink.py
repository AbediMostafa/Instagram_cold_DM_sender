from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class TikTokLink(BaseWithTimeZoneModel):
    name = CharField(null=True)
    offer = CharField(null=True)
    spark_id = CharField(null=True)
    geo = CharField(null=True)
    post_link = TextField()
    error = TextField()
    comments = IntegerField(default=0)
    likes = IntegerField(default=0)
    shares = IntegerField(default=0)
    saves = IntegerField(default=0)
    play_counts = IntegerField(default=0)

    def add_error(self, error):
        self.error = error
        self.save()

    class Meta:
        table_name = 'tik_tok_links'
