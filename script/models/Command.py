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

    @classmethod
    def get_latest_successful_command(cls, account_id, _type, n_minutes_ago):
        return (cls
                .select()
                .where((cls.state == 'success') &
                       (cls.account == account_id) &
                       (cls.type == _type) &
                       (cls.created_at > n_minutes_ago)
                       )
                .order_by(cls.created_at.desc())
                .first())

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
