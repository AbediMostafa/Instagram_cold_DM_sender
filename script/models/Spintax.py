from peewee import *
from .Category import Category
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Spintax(BaseWithTimeZoneModel):
    name = CharField()
    type = CharField()
    text = TextField()

    category = ForeignKeyField(Category, backref='spintaxes', null=True)

    updated_at = DateTimeField(null=True)

    @classmethod
    def get_value(cls, _type, category=None, default=None):
        record = (Spintax
                  .select()
                  .where(
            (Spintax.type == _type) &
            (Spintax.category == category)
        )
                  .first())

        return record.text if record else default

    class Meta:
        table_name = 'spintaxes'
