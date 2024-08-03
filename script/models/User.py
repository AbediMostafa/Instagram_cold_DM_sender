import datetime

from peewee import *
from .Base import BaseModel


class User(BaseModel):
    name = CharField()
    email = CharField()
    password = CharField()

    created_at = DateTimeField(null=True, default=datetime.datetime.now)
    updated_at = DateTimeField(null=True, constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'users'
