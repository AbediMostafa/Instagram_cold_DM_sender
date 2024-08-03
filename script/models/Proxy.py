from peewee import *
from .Base import BaseModel


class Proxy(BaseModel):
    ip = CharField()
    port = IntegerField()
    username = CharField()
    password = CharField()
    state = CharField()

    def deactivate(self):
        self.state = 'inactive'
        self.save()

    class Meta:
        table_name = 'proxies'
