from peewee import *
from .Base import BaseModel
from .Account import Account


class Setting(BaseModel):
    type = CharField()
    key = CharField()
    value = IntegerField()
    description = CharField(null=True)

    @classmethod
    def get_value(cls, _key, default=None):
        record = (Setting
                  .select()
                  .where(Setting.key == _key)
                  .first())

        return record.value if record else default

    class Meta:
        table_name = 'settings'
