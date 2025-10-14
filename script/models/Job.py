# jobs.py
from peewee import *
from .Base import BaseModel


class Job(BaseModel):
    title = CharField()
    is_used = SmallIntegerField(default=0)

    def set_is_used(self, is_used):
        self.is_used = is_used
        self.save()

    class Meta:
        table_name = 'jobs'


def get_free_job():
    """Return one unused job and mark it as used."""
    job = Job.select().where(Job.is_used == 0).order_by(Job.id).first()
    if not job:
        # Reset all jobs to unused if none are free
        Job.update(is_used=0).execute()
        job = Job.select().where(Job.is_used == 0).order_by(Job.id).first()

    if job:
        job.set_is_used(1)
        print(f'Selected job: {job.title}')
        return job

    return None
