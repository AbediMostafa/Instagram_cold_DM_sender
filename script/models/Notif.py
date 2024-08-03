from datetime import datetime

from peewee import *
from .Base import BaseModel
from .Account import Account
from .Lead import Lead
from .Thread import Thread
from .Message import Message


class Notif(BaseModel):
    account = ForeignKeyField(Account, backref='notifs', null=True)
    lead = ForeignKeyField(Lead, backref='notifs', null=True)
    thread = ForeignKeyField(Thread, backref='notifs', null=True)
    message = ForeignKeyField(Message, backref='notifs', null=True)
    visibility = CharField(default='unseen')

    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        table_name = 'notifs'
