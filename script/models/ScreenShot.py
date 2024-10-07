import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account


class ScreenShot(BaseModel):
    cause = CharField()
    path = CharField()
    account = ForeignKeyField(Account, backref='screen_shots')
    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'screen_shots'
