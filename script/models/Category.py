import datetime
from peewee import *
from .Base import BaseModel


class Category(BaseModel):
    title = CharField()
    description = TextField(null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)
    updated_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'categories'
