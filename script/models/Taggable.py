from peewee import *
from .Base import BaseModel
from .Tag import Tag


class Taggable(BaseModel):
    tag = ForeignKeyField(Tag, backref='taggables', on_delete='CASCADE')
    taggable_id = IntegerField()
    taggable_type = CharField()

    @classmethod
    def get_taggable_class(self, model):
        type_mapping = {
            'Lead': r'App\Models\Lead',
            'Account': r'App\Models\Account',
        }

        return type_mapping[model]

    class Meta:
        table_name = 'taggables'
        primary_key = CompositeKey('tag', 'taggable_id', 'taggable_type')


def tag_account(account, tag):
    Taggable.get_or_create(
        tag=tag,
        taggable_id=account.id,
        taggable_type=Taggable.get_taggable_class('Account')
    )
