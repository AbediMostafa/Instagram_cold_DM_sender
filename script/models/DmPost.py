from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Category import Category
from peewee import *


class DmPost(BaseWithTimeZoneModel):
    title = CharField()
    category = ForeignKeyField(Category, backref='lead_sources', null=True)
    description = TextField(null=True)

    class Meta:
        table_name = 'dm_posts'


def get_or_reset_dm_post_for_lead(leads):
    from .DmPostLead import DmPostLead

    # get first lead
    lead = leads[0]

    # Posts this lead used before
    used_dm_post_ids = DmPostLead.select(DmPostLead.dm_post).where(DmPostLead.lead == lead)

    # Find a DmPost didnt see before
    random_unlinked_dm_post = (
        DmPost.select()
        .where(DmPost.id.not_in(used_dm_post_ids))
        .order_by(fn.Random())
        .limit(1)
        .first()
    )

    # Submit and return if exists
    if random_unlinked_dm_post:

        for current_lead in leads:
            DmPostLead.create(dm_post=random_unlinked_dm_post, lead=current_lead)

        return random_unlinked_dm_post

    # If dont delete all Dm post leads of current lead
    for current_lead in leads:
        DmPostLead.delete().where(DmPostLead.lead == current_lead).execute()

    # Get a random post
    random_dm_post = (
        DmPost.select()
        .order_by(fn.Random())
        .limit(1)
        .first()
    )

    # If there's dm post, creat it
    if random_dm_post:
        for current_lead in leads:
            DmPostLead.create(dm_post=random_dm_post, lead=current_lead)
        return random_dm_post

    return None
