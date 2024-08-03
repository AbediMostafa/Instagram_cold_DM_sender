import datetime

from peewee import *
from .Base import BaseModel


class Template(BaseModel):
    text = CharField()
    caption = CharField()
    type = CharField()
    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'templates'

