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
            (Lead.account == account) &
            (Lead.last_state == 'followed')

        )
                          .order_by(fn.Random())
                          .limit(cnt))

        count = leads.count()

        if count < cnt:
            account.add_cli('Warning ==================================================================')
            account.add_cli(f'We should send {cnt} DMs while we have {count} followed leads, increase follow rate')
            account.add_cli('==========================================================================')

        if not leads:
            account.add_cli('Critical state ===========================================================')
            account.add_cli(f"We ran out of followed leads trying to get free leads...")
            account.add_cli('==========================================================================')

            leads = (Lead.select().where(
                (Lead.account_id.is_null(True)) &
                (Lead.last_state == 'free')

            )
                     .order_by(fn.Random())
                     .limit(cnt))

            if not leads:
                account.add_cli('Critical state =====================================')
                account.add_cli(f"We dont have any free leads add more please...")
                account.add_cli('====================================================')

        return leads

    def passed_hours_since_last_follow_up(self):
        return (tehran_now() - self.last_command_send_date).total_seconds() / 3600

    def has_not_reached_dm_send_time_yet(self):
        category = self.category

        return self.passed_hours_since_last_follow_up() < category.hour_interval

    class Meta:
        table_name = 'leads'
