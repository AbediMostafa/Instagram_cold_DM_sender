import traceback
from .BaseActionState import BaseActionState
from script.extra.adapters.SettingAdapter import SettingAdapter

from script.models.Thread import Thread
from script.models.Lead import Lead
from script.models.Message import Message
from script.models.Command import performed_command_count


class GetThreadMessagesEvent(BaseActionState):
    ig_threads = None
    ig_thread = None
    db_thread = None
    ig_user = None
    db_user = None
    ig_message = None
    db_message = None
    performed_commands = None

    def cant(self):
        self.performed_commands = performed_command_count(self.account, ['get thread messages'], 24)
        return self.performed_commands >= SettingAdapter.max_get_threads()

    def init_state(self):
        self.account.add_cli('Getting instagram threads ...')
        self.ig_threads = self.ig.direct_threads(amount=20)
        self.account.add_cli(f'Got {len(self.ig_threads)} recent threads')

    def cant_state(self):
        self.account.add_cli(f"We've sent {self.performed_commands} get threads commands and reached the allowed count")
        pass

    def success_state(self):
        self.account.set_state('get thread messages', 'app_state')
        self.command = self.account.create_command('get thread messages', 'processing')
        for self.ig_thread in self.ig_threads:

            self.handle_thread_user()

            self.db_thread = Thread.select().where(
                (Thread.account == self.account) &
                (Thread.lead == self.db_user)
            ).first()

            if not self.db_thread:
                self.db_thread = Thread.create(
                    account=self.account,
                    lead=self.db_user
                )

            self.check_messages()

        self.command.update_cmd('state', 'success')

    def handle_thread_user(self):
        users = self.ig_thread.users
        self.ig_user = users[0]

        self.db_user = Lead.select().where(Lead.username == self.ig_user.username).first()

        if not self.db_user:
            self.db_user = Lead.create(account=self.account, username=self.ig_user.username)

    def check_messages(self):
        for self.ig_message in reversed(self.ig_thread.messages):

            if self.ig_message.item_type != 'text':
                continue

            # Attempt to decode the surrogate pairs into proper Unicode
            text = self.ig_message.text.encode('utf-16', 'surrogatepass').decode('utf-16')

            self.db_message = Message.select().where(
                (Message.thread == self.db_thread) &
                (Message.text.contains(text.strip()))
            ).first()

            if not self.db_message:
                self.account.add_cli(
                    f'We have new message from {self.ig_user.username} with the txt of : {self.ig_message.text}')

                self.account.add_cli('Starting to create this message')
                self.new_message_process()

    def new_message_process(self):

        state_mapper = {
            'dm follow up': 'unseen dm reply',
            'unseen dm reply': 'unseen dm reply',
            'seen dm reply': 'unseen dm reply',

            'interested': 'interested',
            'not interested': 'not interested',
            'needs response': 'needs response',

            'loom follow up': 'unseen loom reply',
            'unseen loom reply': 'unseen loom reply',
            'seen loom reply': 'unseen loom reply',
            'free': 'free'
        }

        self.db_user.change_state(
            account=self.account,
            state=state_mapper[self.db_user.last_state],
            update_date=True
        )

        self.db_message = Message.create(
            message_id=self.ig_message.id,
            thread=self.db_thread,
            text=self.ig_message.text,
            sender='account' if self.ig_message.is_sent_by_viewer else 'lead',
            type='text' if self.ig_message.item_type == 'text' else 'post',
            state='seen' if self.ig_message.is_sent_by_viewer else 'unseen',
        )

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem Getting tread's messages : {str(e)}")
        self.account.add_log(traceback.format_exc())
