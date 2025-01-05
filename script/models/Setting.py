from peewee import *
from .Base import BaseModel


class Setting(BaseModel):
    type = CharField()
    key = CharField()
    value = TextField()
    description = CharField(null=True)

    @classmethod
    def get_value(cls, _key, default=None):
        record = (Setting
                  .select()
                  .where(Setting.key == _key)
                  .first())

        return record.value if record else default

    @classmethod
    def set_value(cls, _key, _value, _type='text', description=None):
        """
        Set or update the value for a given key.
        If the key exists, update its value. Otherwise, create a new record.
        """
        record, created = cls.get_or_create(
            key=_key,
            defaults={'value': _value, 'type': _type, 'description': description}
        )

        if not created:
            # Update the value and other fields if the record already exists
            record.value = _value
            if _type:
                record.type = _type
            if description:
                record.description = description
            record.save()

    class Meta:
        table_name = 'settings'
