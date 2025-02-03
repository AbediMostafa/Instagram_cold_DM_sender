from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account
from .Lead import Lead
from script.extra.helper import tehran_now


class Loom(BaseWithTimeZoneModel):

    hashed_name = CharField()
    original_name = CharField()
    path = CharField()
    description = TextField(null=True)
    state = CharField(default='pending')

    account = ForeignKeyField(Account, backref='looms', null=True)
    lead = ForeignKeyField(Lead, backref='looms', null=True)

    updated_at = DateTimeField(null=True, default=tehran_now)

    def update_state(self, state):
        self.state = state
        self.save()

    class Meta:
        table_name = 'looms'



