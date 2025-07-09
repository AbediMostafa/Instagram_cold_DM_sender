from peewee import *
from .Base import BaseModel


class AdsPowerLock(BaseModel):
    last_executed_at = DateTimeField(null=False)

    class Meta:
        table_name = 'ads_power_locks'
