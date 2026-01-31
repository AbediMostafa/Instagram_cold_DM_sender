import datetime
from peewee import *
from .Workflow import Workflow
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now


class Process(BaseWithTimeZoneModel):
    pid = BigIntegerField()
    status = CharField(default='idle')
    proxy_type = CharField()
    workflow = ForeignKeyField(Workflow, backref='processes', null=True)
    last_checked_at = DateTimeField(null=True, default=tehran_now)

    stopped_process = ['stopped', 'idle', 'terminated']

    class Meta:
        table_name = 'processes'

    def add_cli(self, log, account=None, print_only=False):
        from .Cli import Cli

        if account:
            log = f'[{self.pid} -- {account.id} -- {account.username}] ${log}'
        else:
            log = f'[{self.pid}] ${log}'

        print(log)

        if print_only:
            return False

        truncated_log = (log[:254]) if log else ''

        Cli.create(account=account, log=truncated_log, process=self)

    @staticmethod
    def update_or_create_process(pid):
        now = tehran_now()

        process, created = Process.get_or_create(
            pid=pid,
            defaults={'last_checked_at': now}
        )

        if not created:
            process.last_checked_at = now
            process.save()

        return process

    def verify(self):
        pass
