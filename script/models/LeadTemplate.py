from peewee import *
from .Base import BaseModel
from .Lead import Lead
from .Template import Template


class LeadTemplate(BaseModel):
    lead = ForeignKeyField(Lead, backref='templates')
    template = ForeignKeyField(Template, backref='lead_template')

    class Meta:
        table_name = 'lead_template'
