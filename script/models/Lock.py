from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now
from datetime import timedelta


class Lock(BaseWithTimeZoneModel):
    name = CharField(unique=True)
    locked_until = DateTimeField(null=True)

    class Meta:
        table_name = 'locks'

    @classmethod
    def acquire(cls, lock_name, duration_seconds=30):
        """
        Try to acquire a lock atomically.
        Returns True if lock acquired, False otherwise.
        """
        now = tehran_now()
        lock_until = now + timedelta(seconds=duration_seconds)

        updated = (
            cls
            .update(locked_until=lock_until)
            .where(
                (cls.name == lock_name) &
                ((cls.locked_until.is_null()) | (cls.locked_until < now))
            )
            .execute()
        )

        return updated > 0

    @classmethod
    def release(cls, lock_name):
        """
        Release a lock.
        """
        cls.update(locked_until=None).where(cls.name == lock_name).execute()
