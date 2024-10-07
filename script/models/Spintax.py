from peewee import *
from .Base import BaseModel
from .Category import Category
from datetime import datetime, timedelta


class Spintax(BaseModel):
    name = CharField()
    type = CharField()
    text = TextField()

    category = ForeignKeyField(Category, backref='spintaxes', null=True)

    created_at = DateTimeField(null=True, default=datetime.now)
    updated_at = DateTimeField(null=True)

    @classmethod
    def get_value(cls, _type, category, default=None):
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
