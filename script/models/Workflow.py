import datetime
from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Service import Service


class Workflow(BaseWithTimeZoneModel):
    title = CharField()

    service = ForeignKeyField(
        Service,
        backref='workflows',
        null=True,
        on_delete='SET NULL'
    )

    # modules = ManyToManyField(
    #     Module,
    #     backref='workflows',
    #     through_model=WorkflowModule
    # )

    def modules(self):
        from .Module import Module
        from .WorkflowModule import WorkflowModule

        return (
            Module
            .select()
            .join(WorkflowModule, on=(WorkflowModule.module_id == Module.id))
            .where(WorkflowModule.workflow_id == self.id)
        )

    class Meta:
        table_name = 'workflows'
