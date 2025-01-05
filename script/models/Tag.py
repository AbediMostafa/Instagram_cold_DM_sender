import datetime
from peewee import *
from .Base import BaseModel
from datetime import datetime, timedelta


class Tag(BaseModel):
    title = CharField()
    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        table_name = 'tags'
