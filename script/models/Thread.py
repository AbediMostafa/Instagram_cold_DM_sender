import datetime

from peewee import *
from .Account import Account
from .Lead import Lead
from .Category import Category
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Thread(BaseWithTimeZoneModel):
    thread_id = CharField()
    thread_url_id = CharField()
    account = ForeignKeyField(Account, backref='threads', null=True)
    lead = ForeignKeyField(Lead, backref='threads', null=True)
    category = ForeignKeyField(Category, backref='threads', null=True)

    class Meta:
        table_name = 'threads'


def get_url_id(lead, account):
    thread = Thread.select().where(
        (Thread.account == account) &
        (Thread.lead == lead)
    ).first()

    return thread.thread_url_id if thread else None
