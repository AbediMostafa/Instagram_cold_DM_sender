from peewee import *
from .Base import BaseModel
from .Account import Account
from .Template import Template


class AccountTemplate(BaseModel):
    account = ForeignKeyField(Account, backref='templates')
    template = ForeignKeyField(Template, backref='account_template')

    class Meta:
        table_name = 'account_template'
