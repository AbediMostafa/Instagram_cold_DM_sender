from peewee import *
from .DmPost import DmPost
from .Lead import Lead
from .Base import BaseModel


class DmPostLead(BaseModel):
    dm_post = ForeignKeyField(DmPost, backref='leads')
    lead = ForeignKeyField(Lead, backref='dm_posts')

    class Meta:
        table_name = 'dm_post_lead'
        indexes = (
            (('dm_post', 'lead'), True),  # Unique constraint on pair
        )
