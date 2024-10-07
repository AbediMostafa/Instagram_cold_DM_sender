import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account
from .Message import Message
from .Lead import Lead


class Command(BaseModel):
    account = ForeignKeyField(Account, backref='commands')
    lead = ForeignKeyField(Lead, backref='commands', null=True)

    commandable_id = IntegerField()
    commandable_type = CharField()

    times = IntegerField()
    type = CharField()
    state = CharField()

    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    def update_cmd(self, col, val):
        setattr(self, col, val)
        self.save()

    @classmethod
    def get_pending_commands(cls, _type):
        return cls.select().where(
            (cls.type == _type) &
            (cls.state == 'pending')
        ).order_by(cls.account_id.desc())

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


def performed_command_count(account, command_types, hours, times=0, state='success'):
    from datetime import datetime, timedelta

    hours_ago = datetime.now() - timedelta(hours=hours)

    return (Command
            .select(fn.COUNT(Command.id).alias('count'))
            .where(
        (Command.account == account) &
        (Command.type.in_(command_types)) &
        (Command.times == times) &
        (Command.state == state) &
        (Command.created_at >= hours_ago)
    )
            .scalar())
