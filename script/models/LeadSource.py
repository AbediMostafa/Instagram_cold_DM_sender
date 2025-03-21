from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Category import Category
from peewee import *


class LeadSource(BaseWithTimeZoneModel):
    title = CharField()
    is_used = SmallIntegerField(default=0)
    category = ForeignKeyField(Category, backref='lead_sources', null=True)

    class Meta:
        table_name = 'lead_sources'


def free_lead_source_query(count, category=None):
    query = LeadSource.select().where(LeadSource.is_used == 0)

    if category:
        query = query.where(LeadSource.category == category)

    return query.order_by(LeadSource.id).limit(count)


def get_lead_source(count, category=None):
    query = free_lead_source_query(count, category)

    # Refresh lead_source if no free lead_source exist
    if not query.exists():
        LeadSource.update(is_used=False).execute()

    lead_sources = query

    if lead_sources.count():
        for lead_source in lead_sources:
            lead_source.is_used = True
            lead_source.save()

    return lead_sources
