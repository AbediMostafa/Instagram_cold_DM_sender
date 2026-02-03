import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


class Module(BaseWithTimeZoneModel):
    title = CharField()
    module_path = CharField()
    class_name = CharField()
    priority = CharField()

    # workflow = ForeignKeyField(
    #     Workflow,
    #     backref='modules',
    #     null=True,
    #     on_delete='SET NULL'
    # )

    def workflows(self):
        from .Workflow import Workflow
        from .WorkflowModule import WorkflowModule

        return (
            Workflow
            .select()
            .join(WorkflowModule, on=(WorkflowModule.workflow_id == Workflow.id))
            .where(WorkflowModule.module_id == self.id)
        )

    class Meta:
        table_name = 'modules'
