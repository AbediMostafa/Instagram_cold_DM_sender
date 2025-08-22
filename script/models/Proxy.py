from peewee import *
from .Base import BaseModel


class Proxy(BaseModel):
    ip = CharField()
    port = IntegerField()
    username = CharField()
    password = CharField()
    state = CharField()
    is_used = SmallIntegerField(default=0)

    # is_used = SmallIntegerField(default=0)

    def deactivate(self):
        self.state = 'inactive'
        self.save()

    class Meta:
        table_name = 'proxies'


def get_free_proxy():
    query = Proxy.select().where(Proxy.is_used == 0)

    if not query.exists():
        Proxy.update(is_used=False).execute()

    next_proxy = (query
                  .order_by(Proxy.id)
                  .first())

    if next_proxy:
        next_proxy.is_used = True
        next_proxy.save()
        print(f'Selected proxy : {next_proxy.ip}')

    return next_proxy
