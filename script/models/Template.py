import datetime

from peewee import *
from .Base import BaseModel


def delete(_type, text):
    return Template.delete().where(
        (Template.type == _type) & (Template.text == text)
    ).execute()


def get_a(_type):
    return Template.select().where(Template.type == _type).first()


class Template(BaseModel):
    text = CharField()
    caption = CharField()
    type = CharField()
    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    class Meta:
        table_name = 'templates'
