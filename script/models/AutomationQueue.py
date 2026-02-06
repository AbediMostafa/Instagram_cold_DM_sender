from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .Account import Account
from playhouse.postgres_ext import JSONField
from box import Box

class AutomationQueue(BaseWithTimeZoneModel):
    account = ForeignKeyField(Account, backref='automation_queues')
    payload = JSONField()  # JSON stored as string
    status = CharField(default='pending')

    @property
    def payload_obj(self):
        return Box(self.payload)
    class Meta:
        table_name = 'automation_queues'

    def set_status_to(self, status):
        self.status = status
        self.save(only=[AutomationQueue.status])

    @classmethod
    def pop_first(cls):
        first_record = (AutomationQueue.select()
                        .where(AutomationQueue.status == 'pending')
                        .order_by(AutomationQueue.id).first())

        if not first_record:
            return None

        first_record.set_status_to('processing')

        return first_record
