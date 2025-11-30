from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from playhouse.postgres_ext import JSONField
from .Base import database


class CharityLead(BaseWithTimeZoneModel):
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    company_name = CharField(null=True)
    phone_number = CharField(null=True)
    website = CharField(null=True)
    email = CharField(null=True)
    lead_type = CharField()
    is_used = SmallIntegerField(default=0)  # corresponds to unsignedTinyInteger
    duplicated_record = SmallIntegerField(default=0)  # corresponds to unsignedTinyInteger
    instagram = CharField(null=True, unique=True)
    linkedin = CharField(null=True, unique=True)
    data = JSONField()  # JSONB stored as text in Peewee
    created_at = DateTimeField()
    updated_at = DateTimeField()

    def set_is_used(self, is_used):
        self.is_used = is_used
        self.save()

    def set_is_duplicated(self, duplicated):
        self.duplicated_record = duplicated
        self.save()

    def save_socials(self, instagram=None, linkedin=None):
        if instagram:
            self.instagram = instagram

        if linkedin:
            self.linkedin = linkedin

        self.save()

    def record_exists(self, instagram=None, linkedin=None):
        query = CharityLead.select()

        if instagram:
            query = query.where(CharityLead.instagram == instagram)
        if linkedin:
            query = query.where(CharityLead.linkedin == linkedin)

        return query.exists()

    class Meta:
        table_name = 'charity_leads'


def get_free_charity_lead():
    next_enriched_lead = (CharityLead
    .select()
    .where(
        (CharityLead.is_used == 0) &
        ((CharityLead.instagram.is_null(True)) | (CharityLead.linkedin.is_null(True)))
    )
    .order_by(CharityLead.id)
    .first())

    if not next_enriched_lead:
        return None

    next_enriched_lead.set_is_used(1)

    print(f'Selected enriched lead : {next_enriched_lead.id}')

    return next_enriched_lead
