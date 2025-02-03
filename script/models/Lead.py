import datetime
from peewee import *
from .Account import Account
from dotenv import load_dotenv
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
import os
import requests


class Lead(BaseWithTimeZoneModel):
    username = CharField()
    instagram_id = BigIntegerField(null=True)
    times = IntegerField(default=0)
    last_state = CharField(default='free')
    account = ForeignKeyField(Account, backref='leads', null=True)

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
    def get_leads(cls, count=1):
        load_dotenv()

        data = {
            'username': os.getenv('API_USERNAME'),
            'password': os.getenv('API_PASSWORD'),
            'number_of_leads': count,
        }

        response = requests.post(os.getenv('GET_LEAD_API_URL'), data=data)

        if response.status_code == 200:
            leads = []

            for response_lead in response.json():
                lead_id = response_lead['id']
                leads.append(cls.get_by_id(lead_id))

            return leads

    @classmethod
    def get_unfollowed_leads(cls, account, cnt):
        from .Command import Command

        # Subquery to find leads that have been followed by the account
        followed_leads = Command.select(Command.lead_id).where(
            (Command.account == account) &
            (Command.type == 'follow')
        )

        # Query to find leads that have not been followed by the account
        unfollowed_leads = Lead.select().where(
           Lead.id.not_in(followed_leads)
        ).limit(cnt)

        return list(unfollowed_leads)

    class Meta:
        table_name = 'leads'
