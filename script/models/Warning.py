from peewee import *
from .Account import Account
from datetime import  timedelta
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now


class Warning(BaseWithTimeZoneModel):
    cause = TextField(null=True)
    duration = IntegerField(default=24)
    account = ForeignKeyField(Account, backref='warnings', null=True)

    def get_expiry_time(self):
        return self.created_at + timedelta(hours=self.duration)

    def expiration_time_not_passed(self):
        return tehran_now() < self.get_expiry_time()

    def get_hours_until_expiry(self):
        time_remaining = self.get_expiry_time() - tehran_now()
        return time_remaining.total_seconds() // 3600

    class Meta:
        table_name = 'warnings'
