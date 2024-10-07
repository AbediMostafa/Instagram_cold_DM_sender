from datetime import datetime
from peewee import *
from .Base import BaseModel
from .Account import Account
from datetime import datetime, timedelta


class Warning(BaseModel):
    cause = TextField(null=True)
    duration = IntegerField(default=24)
    account = ForeignKeyField(Account, backref='warnings', null=True)

    created_at = DateTimeField(null=True, default=datetime.now)

    def get_expiry_time(self):
        return self.created_at + timedelta(hours=self.duration)

    def expiration_time_not_passed(self):
        return datetime.now() < self.get_expiry_time()

    def get_hours_until_expiry(self):
        time_remaining = self.get_expiry_time() - datetime.now()
        return time_remaining.total_seconds() // 3600

    class Meta:
        table_name = 'warnings'
