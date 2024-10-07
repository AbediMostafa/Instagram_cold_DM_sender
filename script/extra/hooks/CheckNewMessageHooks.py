from script.models.Thread import Thread
from script.models.Lead import Lead
from script.models.Message import Message
from script.models.Notif import Notif


class CheckNewMessageHooks:
    account = None
    ig = None
    ig_threads = None
    ig_thread = None
    db_thread = None
    ig_user = None
    db_user = None
    ig_message = None
    db_message = None

    def __init__(self, account, ig):
        self.account = account
        self.ig = ig
        self.account.add_cli(f'Starting the process of finding new messages of {self.account.username}')
        self.get_ig_threads()
        self.check_for_new_messages()

    def get_ig_threads(self):
        self.account.add_cli('Getting instagram threads ...')
        self.ig_threads = self.ig.direct_threads(amount=20)
        self.account.add_cli(f'Got {len(self.ig_threads)} recent threads')

    def check_for_new_messages(self):

        for self.ig_thread in self.ig_threads:
            self.get_thread_record()
            self.handle_thread_user()

            if not self.db_thread:
                self.create_thread()

            self.check_messages()

    def create_thread(self):
        self.db_thread = Thread.create(
            thread_id=self.ig_thread.id,
            account=self.account,
            lead=self.db_user
        )

    def check_messages(self):
        for self.ig_message in reversed(self.ig_thread.messages):

            if self.ig_message.item_type != 'text':
                continue

            self.db_message = Message.select().where(Message.message_id == self.ig_message.id).first()

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

    def get_thread_record(self):
        self.db_thread = Thread.select().where(Thread.thread_id == self.ig_thread.id).first()

    def handle_thread_user(self):
        users = self.ig_thread.users
        self.ig_user = users[0]

        self.get_user_record()

        if not self.db_user:
            self.create_lead()

    def get_user_record(self):
        self.db_user = Lead.select().where(Lead.username == self.ig_user.username).first()

    def create_lead(self):
        self.db_user = Lead.create(account=self.account, username=self.ig_user.username)
