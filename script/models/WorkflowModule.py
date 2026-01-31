import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Module import Module
from .Service import Service
from .Workflow import Workflow


class WorkflowModule(BaseWithTimeZoneModel):
    workflow = ForeignKeyField(
        Workflow,
        backref='workflow_modules',
        on_delete='CASCADE'
    )
    module = ForeignKeyField(
        Module,
        backref='module_workflows',
        on_delete='CASCADE'
    )

    class Meta:
        table_name = 'workflow_module'
        indexes = (
            (('workflow', 'module'), True),  # unique pair (important)
        )
