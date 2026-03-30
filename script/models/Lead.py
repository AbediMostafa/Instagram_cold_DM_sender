import datetime
from peewee import *
from .Account import Account
from .Category import Category
from dotenv import load_dotenv
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
import os
import requests
from script.extra.helper import tehran_now


class Lead(BaseWithTimeZoneModel):
    username = CharField()
    instagram_id = BigIntegerField(null=True)
    times = IntegerField(default=0)
    last_state = CharField(default='free')
    account = ForeignKeyField(Account, backref='leads', null=True)
    category = ForeignKeyField(Category, backref='leads', null=True)

    last_command_send_date = DateTimeField(null=True)

    def set_account(self, account):
        account.add_cli('Saving lead for account ...')
        self.account = account
        self.save()

    def update_instagram_id(self, instagram_id):
        self.instagram_id = instagram_id
        self.save()

    def change_state(self, account=None, state=None, add_history=None, times=0, update_date=None, user=None):
        from script.extra.helper import tehran_now

        if account:
            self.account = account

        if state:
            self.last_state = state

        if update_date:
            self.last_command_send_date = tehran_now()

        self.times = times

        if add_history:
            self.add_history(state, account, times, user)

        self.save()

    def change_state_from_free(self, state, account, times=0, user=None):

        if self.last_state in ['free', 'followed']:
            self.set_state(state)

        self.add_history(state, account, times, user)

    def set_state(self, state, times=0):
        self.last_state = state
        self.times = times
        self.save()

    def add_history(self, state, account=None, times=0, user=None):
        from .LeadHistory import LeadHistory

        LeadHistory.create(
            state=state,
            times=times,
            lead=self,
            account=account.id,
            user=user)

    @classmethod
    def get_leads(cls, count=1, category=None):
        load_dotenv()

        data = {
            'username': os.getenv('API_USERNAME'),
            'password': os.getenv('API_PASSWORD'),
            'number_of_leads': count,
            'category': category,
        }

        response = requests.post(os.getenv('GET_LEAD_API_URL'), data=data)

        if response.status_code == 200:
            leads = []

            for response_lead in response.json():
                lead_id = response_lead['id']
                leads.append(cls.get_by_id(lead_id))

            return leads

    @classmethod
    def get_leads_for_follow(cls, cnt):

        return (Lead.select().where(
            (Lead.account_id.is_null(True)) &
            (Lead.last_state == 'free')

        )
                .order_by(fn.Random())
                .limit(cnt))

    @classmethod
    def get_leads_for_dm(cls, account, cnt):

        leads = (Lead.select().where(
            (Lead.account_id.is_null(True)) &
            (Lead.last_state == 'free')
        )
                 .order_by(fn.Random())
                 .limit(cnt))

        count = leads.count()

        if count < cnt:
            account.add_cli('Warning =============================================')
            account.add_cli(f'We should send {cnt} DMs while we have {count} leads')
            account.add_cli('=====================================================')

        if not leads:
            account.add_cli('Critical state ===========================================================')
            account.add_cli(f"We ran out of followed leads trying to get free leads...")
            account.add_cli('==========================================================================')

        return leads

    @classmethod
    def get_leads_for_api_dm(cls, cnt):

        return (Lead.select().where(
            (Lead.account_id.is_null(True)) &
            (Lead.instagram_id.is_null(False)) &
            (Lead.last_state == 'free')
        )
                .order_by(fn.Random())
                .limit(cnt))

    @classmethod
    def get_without_pk_leads(cls, cnt):

        return (Lead.select().where(
            (Lead.account_id.is_null(True)) &
            (Lead.instagram_id.is_null(True)) &
            (Lead.last_state == 'free')
        )
                .order_by(fn.Random())
                .limit(cnt))

    def passed_hours_since_last_follow_up(self):
        return (tehran_now() - self.last_command_send_date).total_seconds() / 3600

    def has_not_reached_dm_send_time_yet(self):
        category = self.category

        return self.passed_hours_since_last_follow_up() < category.hour_interval

    @classmethod
    def select_lead_for_profile(cls, account):

        lead = Lead.select().where(Lead.account == account).first()

        if lead:
            account.add_cli(f'We have a reserved lead for this account : {lead.username}')
            return lead

        account.add_cli('Theres no reserved lead for this account, getting new one ...')

        return (Lead.select().where(
            (Lead.account_id.is_null(True)) &
            (Lead.instagram_id.is_null(False))
        )
                .order_by(fn.Random())
                .first())

    @classmethod
    def get_a_template(cls, account, _type):
        from .Template import Template
        from .LeadTemplate import LeadTemplate

        lead = Lead.select_lead_for_profile(account)

        template = (
            Template
            .select()
            .join(LeadTemplate)
            .where(
                (LeadTemplate.lead == lead) &
                (Template.type == _type)
            )
            .first()
        )

        return template, lead

    @classmethod
    def get_a_media(cls, account, types):
        from .Template import Template
        from .LeadTemplate import LeadTemplate
        from .AccountTemplate import AccountTemplate

        lead = Lead.select_lead_for_profile(account)

        selected_templates_subquery = (AccountTemplate
                                       .select(AccountTemplate.template)
                                       .where(AccountTemplate.account == account))

        template = (
            Template
            .select()
            .join(LeadTemplate)
            .where(
                (LeadTemplate.lead == lead) &
                (Template.type.in_(types)) &
                (Template.id.not_in(selected_templates_subquery))
            )
            .order_by(Template.id.desc())
        ).first()

        if template is None:
            account.add_cli('Theres no media for this lead ...')
            return None, None, None

        if template.type == 'carousel' or template.type == 'video-post':
            # If media type is carousel OR video-post we need to fetch a set of medias not only first
            medias = (Template
                      .select()
                      .where(Template.carousel_id == template.carousel_id)
                      .order_by(Template.uid))

            return medias, template.type, lead

        # If single media (image/video) → wrap in list
        return [template], template.type, lead

    class Meta:
        table_name = 'leads'
