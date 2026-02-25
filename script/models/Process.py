import datetime
import os
from peewee import *
from .Workflow import Workflow
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now
from dotenv import load_dotenv

load_dotenv()


class Process(BaseWithTimeZoneModel):
    pid = BigIntegerField()
    server_ip = CharField(max_length=45)
    status = CharField(default='idle')
    proxy_type = CharField()
    workflow = ForeignKeyField(Workflow, backref='processes', null=True)
    last_checked_at = DateTimeField(null=True, default=tehran_now)

    stopped_process = ['stopped', 'idle', 'terminated']

    class Meta:
        table_name = 'processes'
        indexes = (
            (('pid', 'server_ip'), True),
        )

    def add_cli(self, log, account=None, print_only=False):
        from .Cli import Cli

        if account:
            log = f'[{self.pid} -- {account.id} -- {account.username}] ${log}'
        else:
            log = f'[{self.pid}] ${log}'

        print(log)
        return False

        if print_only:
            return False

        truncated_log = (log[:254]) if log else ''

        Cli.create(account=account, log=truncated_log, process=self)

    @staticmethod
    def get_server_ip():
        return os.getenv('SERVER_IP', '0.0.0.0')

    @staticmethod
    def update_or_create_process(pid):
        now = tehran_now()
        server_ip = Process.get_server_ip()

        process, created = Process.get_or_create(
            pid=pid,
            server_ip=server_ip,
            defaults={'last_checked_at': now}
        )

        if not created:
            process.last_checked_at = now
            process.save()

        return process

    def verify(self):
        pass