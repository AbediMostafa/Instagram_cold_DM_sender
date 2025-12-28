import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Workflow import Workflow


class Module(BaseWithTimeZoneModel):
    title = CharField()
    module_path = CharField()
    class_name = CharField()

    workflow = ForeignKeyField(
        Workflow,
        backref='modules',
        null=True,
        on_delete='SET NULL'
    )

    class Meta:
        table_name = 'modules'
