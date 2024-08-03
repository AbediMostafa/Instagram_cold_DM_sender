import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account
from .Lead import Lead

class Loom(BaseModel):

    hashed_name = CharField()
    original_name = CharField()
    path = CharField()
    description = TextField(null=True)
    state = CharField(default='pending')

    account = ForeignKeyField(Account, backref='looms', null=True)
    lead = ForeignKeyField(Lead, backref='looms', null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)
    updated_at = DateTimeField(null=True, default=datetime.datetime.now)

    def update_state(self, state):
        self.state = state
        self.save()

    class Meta:
        table_name = 'looms'



