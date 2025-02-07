import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account
from .Message import Message
from .Category import Category
from .Lead import Lead
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import hours_ago


class Command(BaseWithTimeZoneModel):
    account = ForeignKeyField(Account, backref='commands')
    lead = ForeignKeyField(Lead, backref='commands', null=True)
    category = ForeignKeyField(Category, backref='commands', null=True)

    commandable_id = IntegerField()
    commandable_type = CharField()

    times = IntegerField()
    type = CharField()
    state = CharField()

    def update_cmd(self, col, val):
        setattr(self, col, val)
        self.save()

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
    time_threshold = hours_ago(hours)

    return (Command
            .select(fn.COUNT(Command.id).alias('count'))
            .where(
        (Command.account == account) &
        (Command.type.in_(command_types)) &
        (Command.times == times) &
        (Command.state == state) &
        (Command.created_at >= time_threshold)
    )
            .scalar())


def sent_recent_command_within(account, _types, hours=24):
    """
    Check if any successful post command (image, video, or carousel) was sent within the last `hours`.
    """
    time_threshold = hours_ago(hours)

    return (Command
            .select()
            .where(
        (Command.account == account) &
        (Command.type.in_(_types)) &
        (Command.state == 'success') &
        (Command.created_at >= time_threshold)
    )
            .exists())
