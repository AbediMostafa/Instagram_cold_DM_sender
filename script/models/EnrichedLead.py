from peewee import *
from .Base import BaseModel


class EnrichedLead(BaseModel):
    company_name = CharField(null=True)
    about_us = TextField(null=True)
    website = CharField(null=True)
    linkedin_url = CharField(null=True)
    industry = CharField(null=True)
    company_size = CharField(null=True)
    headquarters = CharField(null=True)
    type = CharField(null=True)
    founded = CharField(null=True)
    specialties = CharField(null=True)
    instagram_username = CharField(null=True)
    is_used = SmallIntegerField(default=0)


    class Meta:
        table_name = 'enriched_leads'

    def fill(self, **kwargs):
        """
        Fill multiple fields at once and save.
        Example:
            lead.fill(
                company_name='google',
                website='https://google.com',
                industry='AI Research',
                founded='2015'
            )
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self

    def set_is_used(self, is_used):
        self.is_used = is_used
        self.save()

def get_free_enriched_lead():

    query = EnrichedLead.select().where(
        (EnrichedLead.is_used == 0) & (EnrichedLead.instagram_username.is_null(False))
    )

    if not query.exists():
        EnrichedLead.update(is_used=0).execute()

    next_enriched_lead = query.order_by(EnrichedLead.id).first()

    if not next_enriched_lead:
        return None

    next_enriched_lead.set_is_used(1)

    print(f'Selected enriched lead, instagram : {next_enriched_lead.instagram_username}, company name : {next_enriched_lead.company_name}')

    return next_enriched_lead
