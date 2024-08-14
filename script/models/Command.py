import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account
from .Message import Message
from .Lead import Lead
from datetime import datetime, timedelta


class Command(BaseModel):
    account = ForeignKeyField(Account, backref='commands')
    lead = ForeignKeyField(Lead, backref='commands', null=True)

    commandable_id = IntegerField()
    commandable_type = CharField()

    times = IntegerField()
    type = CharField()
    state = CharField()

    created_at = DateTimeField(null=True, default=datetime.now)

    def update_cmd(self, col, val):
        setattr(self, col, val)
        self.save()

    @classmethod
    def successful_commands_within_passed_24hours(cls, account, _type):
        twenty_hours_ago = datetime.now() - timedelta(hours=24)

        return (cls
                .select(fn.COUNT(cls.id).alias('count'))
                .where(
            (cls.account == account) &
            (cls.type == _type) &
            (cls.state == 'success') &
            (cls.created_at >= twenty_hours_ago)
        )
                .scalar())

    def get_commandable(self):
        model_class = self.get_model_from_type()

        return model_class.get_by_id(self.commandable_id) if model_class else None

    def get_model_from_type(self):
        # This method should return the model class based on the commandable_type
        type_mapping = {
            'App\\Models\\Message': Message,
        }

        return type_mapping.get(self.commandable_type)

    class Meta:
        table_name = 'commands'
