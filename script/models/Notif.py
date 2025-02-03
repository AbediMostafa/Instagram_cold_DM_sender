from datetime import datetime

from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account
from .Lead import Lead
from .Thread import Thread
from .Message import Message


class Notif(BaseWithTimeZoneModel):
    account = ForeignKeyField(Account, backref='notifs', null=True)
    lead = ForeignKeyField(Lead, backref='notifs', null=True)
    thread = ForeignKeyField(Thread, backref='notifs', null=True)
    message = ForeignKeyField(Message, backref='notifs', null=True)
    visibility = CharField(default='unseen')


    class Meta:
        table_name = 'notifs'
