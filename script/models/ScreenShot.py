from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account


class ScreenShot(BaseWithTimeZoneModel):
    cause = CharField()
    path = CharField()
    account = ForeignKeyField(Account, backref='screen_shots')

    class Meta:
        table_name = 'screen_shots'
