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

    commandable_id = IntegerField(null=True)
    commandable_type = CharField(null=True)

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

    def get_url(self):
        from .Url import Url
        try:
            return Url.get(Url.command == self)
        except Url.DoesNotExist:
            return None

    def set_url(self, url_string):
        from .Url import Url  # Lazy import
        url, created = Url.get_or_create(
            command=self,
            defaults={'url': url_string}
        )
        if not created:
            url.url = url_string
            url.save()
        return url

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


def find_posts_to_comment(account_id):
    from .Url import Url

    return (Command
            .select()
            .join(Url, on=(Url.command == Command.id))
            .where(
                (Command.type == 'post image and comment') &
                (Command.state == 'success') &
                (Command.times.in_([0, 1, 2])) &
                (Command.account != account_id) &
                (
                    (Command.commandable_id.is_null()) |
                    (Command.commandable_id != account_id)
                )
            )
            .order_by(Command.created_at.asc())
            .first())
