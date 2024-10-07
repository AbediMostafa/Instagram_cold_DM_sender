from peewee import *
from .Base import BaseModel
import json
from datetime import datetime, timedelta
from .Proxy import Proxy
from .Category import Category
from .Color import Color, get_next_color
import random


class Account(BaseModel):
    proxy = ForeignKeyField(Proxy, backref='accounts', null=True)
    color = ForeignKeyField(Color, backref='accounts', null=True)
    category = ForeignKeyField(Category, backref='accounts', null=True)

    secret_key = CharField(null=True)
    username = CharField(unique=True)
    password = CharField()
    name = CharField(null=True)
    bio = TextField(null=True)
    profile_pic_url = TextField(null=True)
    instagram_state = CharField(default='active')
    app_state = CharField(default='idle')
    avatar_changed = SmallIntegerField(default=0)
    username_changed = SmallIntegerField(default=0)
    initial_posts_deleted = SmallIntegerField(default=0)
    is_used = SmallIntegerField(default=0)
    is_active = SmallIntegerField(default=1)
    web_session = TextField(null=True)
    mobile_session = TextField(null=True)
    log = TextField(null=True)
    created_at = DateTimeField(null=True, default=datetime.now)
    updated_at = DateTimeField(null=True)
    last_login = DateTimeField(null=True)
    next_login = DateTimeField(null=True)

    passed_days_since_creation = 0

    def set_state(self, state='suspended', _type='instagram_state', log=-1):

        setattr(self, _type, state)

        if log != -1:
            self.log = log

        # Save the instance with the new state
        self.save()
        # self.save(only=[Account._type, Account.log] if log != -1 else [Account._type])

    def add_warning(self, cause, duration=24):
        from .Warning import Warning

        Warning.create(account=self, cause=cause, duration=duration)

    def add_log(self, log):
        from .Log import Log

        Log.create(account=self, log=log)

    def add_cli(self, log):
        from .Cli import Cli

        log = f'[{self.username} -- {self.id}] ${log}'

        print(log)
        self.log = log
        self.save()

        Cli.create(account=self, log=log)

    def add_screen_shot(self, cause, path):
        from .ScreenShot import ScreenShot

        ScreenShot.create(
            account=self,
            cause=cause,
            path=path,
        )

    def has(self, prop):
        return getattr(self, prop)

    def get_mobile_session(self):
        try:
            return json.loads(self.mobile_session)
        except:
            return {}

    def save_mobile_session(self, dict_session):
        self.mobile_session = json.dumps(dict_session)
        self.save()

    def save_session(self, session_data):
        self.web_session = json.dumps(session_data)
        self.save()

    def should_not_post(self, command_type, hours=24):
        from .Command import Command

        n_hours_ago = datetime.now() - timedelta(hours=hours)

        return Command.select().where(
            (Command.account_id == self.id) &
            (Command.type == command_type) &
            (Command.state == 'success') &
            (Command.created_at >= n_hours_ago)
        ).exists()

    def get_a_free_template(self, type):
        from .Template import Template
        from .AccountTemplate import AccountTemplate

        return (Template.select().where(
            (Template.type == type) &
            (Template.category == self.category) &
            ~(Template.id << (AccountTemplate
                              .select(AccountTemplate.template)
                              .join(Template)
                              .where((AccountTemplate.account == self) &
                                     (Template.type == type))
                              ))
        )
                .order_by(fn.Rand())
                .first())

    def attach_template(self, template):
        from .AccountTemplate import AccountTemplate

        return AccountTemplate.create(account=self, template=template)

    def create_command(self, _type, state, lead=None, times=0):
        from .Command import Command

        return Command.create(
            account=self,
            type=_type,
            state=state,
            lead=lead,
            times=times,
            created_at=datetime.now()
        )

    def set(self, col, value):
        setattr(self, col, value)
        self.save()

    def get_passed_days_since_creation(self):
        if not self.created_at:
            self.created_at = datetime.now()
            self.save()

        self.passed_days_since_creation = (datetime.now() - self.created_at).days

        self.passed_days_since_creation = 0 if self.passed_days_since_creation < 0 else self.passed_days_since_creation

    def change_proxy(self):
        from .AccountHelper import get_first_proxy_with_less_accounts

        self.proxy = get_first_proxy_with_less_accounts(
            [self.proxy.id]) if self.proxy else get_first_proxy_with_less_accounts()

        if not self.proxy:
            raise Exception('No Proxy left, try to add more')

        self.save()
        return self.proxy

    def get_proxy(self):
        from .AccountHelper import get_first_proxy_with_less_accounts

        if self.proxy:
            return self.proxy

        self.proxy = get_first_proxy_with_less_accounts()

        if not self.proxy:
            raise Exception('No Proxy left, try to add more')

        self.save()
        return self.proxy

    def get_verification_code(self):
        if not self.secret_key:
            return ""

        try:
            import requests
            from script.extra.adapters.RequestAdapter import RequestAdapter
            response = requests.get(RequestAdapter.bulkacc_api(self.secret_key))
            return response.json()['data']['otp']

            time_remaining = 0

            while time_remaining < 6:
                time_remaining = response.json()['data']['timeRemaining']

            return response.json()['data']['otp']

        except:
            pass

    def add_direct(self, text, lead, direct, sender='account', type='text'):
        from .Thread import Thread
        from .Message import Message

        def add_message(th):
            return Message.create(message_id=direct.id, thread=th, text=text, sender=sender, type=type)

        thread = Thread.select().where(Thread.thread_id == direct.thread_id).first()

        if thread:
            return add_message(thread)

        thread = Thread.select().where(
            (Thread.account == self) &
            (Thread.lead == lead)
        ).first()

        if thread:
            return add_message(thread)

        thread = Thread.create(account=self, lead=lead, thread_id=direct.thread_id)
        return add_message(thread)

    def add_direct_url_id(self, text, lead, thread_url_id=None, sender='account', type='text'):
        from .Thread import Thread
        from .Message import Message

        def add_message(th):
            return Message.create(thread=th, text=text, sender=sender, type=type)

        if thread_url_id:
            thread = Thread.select().where(Thread.thread_url_id == thread_url_id).first()

            if thread:
                return add_message(thread)

        thread = Thread.select().where(
            (Thread.account == self) &
            (Thread.lead == lead)
        ).first()

        if thread:
            return add_message(thread)

        thread = Thread.create(account=self, lead=lead, thread_url_id=thread_url_id)
        return add_message(thread)

    def get_latest_warning(self):
        from script.models.Warning import Warning

        return (Warning
                .select()
                .where(Warning.account == self)
                .order_by(Warning.created_at.desc())
                .first())

    def update_last_activity(self):
        from script.extra.adapters.SettingAdapter import SettingAdapter

        random_second = random.randint(1, 59)
        random_minute = random.randint(1, 59)
        random_hour = random.randint(SettingAdapter.minimum_time_for_next_login(),
                                     SettingAdapter.maximum_time_for_next_login())

        time_delta = timedelta(seconds=random_second, minutes=random_minute, hours=random_hour)
        new_time = datetime.now() + time_delta

        self.next_login = new_time
        self.save()

        return new_time

    def next_login_has_not_reached_yet(self):
        if not self.next_login:
            return False, 0

        time_delta = max(self.next_login - datetime.now(), timedelta(0))
        return self.next_login > datetime.now(), time_delta

    def get_color(self):
        if not self.color:
            self.color = get_next_color()
            self.save()

        self.add_cli(f"Account's color : {self.color.title}")
        return self.color

    def get_a_carousel(self):
        from .AccountTemplate import AccountTemplate
        from .Template import Template

        selected_templates_subquery = (AccountTemplate
                                       .select(AccountTemplate.template)
                                       .where(AccountTemplate.account == self))

        # get a single free carousel
        available_carousel = (Template
                              .select()
                              .where(
            (Template.type == 'carousel') &
            (Template.color == self.get_color()) &
            (Template.category == self.category) &
            (~(Template.id << selected_templates_subquery))
        )
                              .order_by(fn.Rand())
                              .first())

        # return series of carousels
        return (Template
                .select()
                .where(Template.carousel_id == available_carousel.carousel_id)
                .order_by(Template.uid)) if available_carousel else None

    def get_a_video(self):
        from .AccountTemplate import AccountTemplate
        from .Template import Template

        selected_templates_subquery = (AccountTemplate
                                       .select(AccountTemplate.template)
                                       .where(AccountTemplate.account == self))

        # get a single free carousel
        video_template = (Template
        .select()
        .where(
            (Template.type == 'video-post') &
            (Template.sub_type == 'video') &
            (~(Template.id << selected_templates_subquery)) &
            (Template.id.not_in([19525, 19526]))
        )).first()

        if not video_template:
            return None, None

        image_template = (Template
                          .select()
                          .where(
            (Template.carousel_id == video_template.carousel_id) &
            (Template.sub_type == 'image') &  # Ensure it's an image subtype
            (Template.type == 'video-post')  # Ensure it's a part of a video-post
        )
                          .first())

        return image_template, video_template,

    def get_latest_post_commands(self, limit=3):
        from .Command import Command

        """
        Fetch the latest `limit` post commands (image, video, or carousel) for the account.
        """
        return (Command
                .select()
                .where(
            (Command.account == self) &
            (Command.type.in_(['post image', 'post video', 'post carousel'])) &
            (Command.state == 'success')  # Ensure we're looking at successful commands
        )
                .order_by(Command.created_at.desc())
                .limit(limit)
                )

    def sent_recent_post_command_within(self, hours=20):
        from .Command import Command

        """
        Check if any successful post command (image, video, or carousel) was sent within the last `hours`.
        """
        time_threshold = datetime.now() - timedelta(hours=hours)

        return (Command
                .select()
                .where(
            (Command.account == self) &
            (Command.type.in_(['post image', 'post video', 'post carousel'])) &
            (Command.state == 'success') &
            (Command.created_at >= time_threshold)
        )
                .exists())

    def determine_next_post_command(self):
        """
        Determine the next post command type based on the latest post commands.
        """
        if self.sent_recent_post_command_within(random.randint(40, 50)):
            return None  # No post can be sent if one was sent

        # Fetch the latest three post commands
        latest_commands = self.get_latest_post_commands()

        # If no commands found, send 'post carousel' as default
        if not latest_commands:
            return 'post carousel'

        # Extract the types of the last commands (we'll have 0 to 3 depending on the data)
        latest_command_types = [cmd.type for cmd in latest_commands]

        # Check conditions based on the number of latest commands found
        if len(latest_command_types) == 3:
            # If the last two commands are 'carousel' and the 3rd last is 'video'
            if latest_command_types[0] == 'post carousel' and latest_command_types[1] == 'post carousel' and \
                    latest_command_types[2] == 'post video':
                return 'post image'
            # If the last two commands are 'carousel' and the 3rd last is 'image'
            elif latest_command_types[0] == 'post carousel' and latest_command_types[1] == 'post carousel' and \
                    latest_command_types[2] == 'post image':
                return 'post video'

            elif latest_command_types[0] == 'post carousel' and latest_command_types[1] == 'post carousel':
                return 'post image'

        elif len(latest_command_types) == 2:
            # If the last two commands are 'carousel'
            if latest_command_types[0] == 'post carousel' and latest_command_types[1] == 'post carousel':
                return 'post image'

        # Default action if none of the specific conditions match
        return 'post carousel'

    class Meta:
        table_name = 'accounts'
