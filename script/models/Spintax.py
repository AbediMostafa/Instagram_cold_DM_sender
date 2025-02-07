from peewee import *
from .Category import Category
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Spintax(BaseWithTimeZoneModel):
    name = CharField()
    times = IntegerField()
    text = TextField()
    category = ForeignKeyField(Category, backref='commands', null=True)

    updated_at = DateTimeField(null=True)

    @classmethod
    def get_value(cls, times, category=None, default=None):
        query = Spintax.select().where(Spintax.times == times)

        if category is not None:
            query = query.where(Spintax.category == category)

        record = query.first()

        return record.text if record else default

    class Meta:
        table_name = 'spintaxes'
