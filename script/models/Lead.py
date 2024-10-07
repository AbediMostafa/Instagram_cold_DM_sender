import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account


class Lead(BaseModel):
    username = CharField()
    instagram_id = BigIntegerField(null=True)
    times = IntegerField(default=0)
    last_state = CharField(default='free')
    account = ForeignKeyField(Account, backref='leads', null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)
    last_command_send_date = DateTimeField(null=True, constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    def set_account(self, account):
        self.account = account
        self.save()

    def update_instagram_id(self, instagram_id):
        self.instagram_id = instagram_id
        self.save()

    def change_state(self, account=None, state=None, add_history=None, times=0, update_date=None, user=None):
        if account:
            self.account = account

        if state:
            self.last_state = state

        if update_date:
            self.last_command_send_date = datetime.datetime.now()

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

    class Meta:
        table_name = 'leads'
