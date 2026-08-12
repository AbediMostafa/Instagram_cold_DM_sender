import datetime
import os
from peewee import *
from .Workflow import Workflow
from .Mobile import Mobile
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

    # Which cloud phone this worker drives. Null for web workers, which are
    # interchangeable; a mobile worker is pinned to one device for its life.
    mobile = ForeignKeyField(Mobile, backref='processes', null=True)

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

    @staticmethod
    def register_mobile_worker(pid, mobile):
        """
        Register a mobile worker in the same table as web workers, pinned to
        its device.

        The row is keyed by (pid, server_ip) like any process, so a restart
        creates a fresh row. To spare the operator re-assigning a workflow to
        every device after each restart, the workflow of the most recent
        previous row for the same device on this server is carried over; the
        panel remains the only place it's ever chosen.
        """
        process = Process.update_or_create_process(pid)

        changed = False

        if process.mobile_id != mobile.id:
            process.mobile = mobile
            changed = True

        if process.workflow_id is None:
            previous = (
                Process
                .select()
                .where(
                    (Process.mobile == mobile) &
                    (Process.server_ip == process.server_ip) &
                    (Process.id != process.id) &
                    (Process.workflow.is_null(False))
                )
                .order_by(Process.id.desc())
                .first()
            )
            if previous is not None:
                process.workflow = previous.workflow_id
                changed = True

        if changed:
            process.save()

        return process

    def verify(self):
        pass