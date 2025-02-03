from peewee import *
import json
from datetime import datetime, timedelta
from .Proxy import Proxy
from .Category import Category
from .Profile import Profile
from .Color import Color, get_next_color
from .ScreenResolution import ScreenResolution, get_next_screen_resolution
import random
from dotenv import load_dotenv
import os
import requests
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now, hours_ago, get_dm_chunk, calculate_daily_dms


class Account(BaseWithTimeZoneModel):
    proxy = ForeignKeyField(Proxy, backref='accounts', null=True)
    color = ForeignKeyField(Color, backref='accounts', null=True)
    screen_resolution = ForeignKeyField(ScreenResolution, backref='accounts', null=True)
    category = ForeignKeyField(Category, backref='accounts', null=True)
    profile = ForeignKeyField(Profile, backref='accounts', null=True)

    secret_key = CharField(null=True)
    username = CharField(unique=True)
    password = CharField()
    name = CharField(null=True)
    bio = TextField(null=True)
    email = TextField(null=True)
    profile_pic_url = TextField(null=True)
    instagram_state = CharField(default='active')
    app_state = CharField(default='idle')
    avatar_changed = SmallIntegerField(default=0)
    username_changed = SmallIntegerField(default=0)
    initial_posts_deleted = SmallIntegerField(default=0)
    has_enough_posts = SmallIntegerField(default=0)
    is_used = SmallIntegerField(default=0)
    is_active = SmallIntegerField(default=1)
    is_public = SmallIntegerField(default=0)
    web_session = TextField(null=True)
    mobile_session = TextField(null=True)
    log = TextField(null=True)
    updated_at = DateTimeField(null=True)
    next_login = DateTimeField(null=True)

    # Possibilities
    passed_days_since_creation = None
    allowed_number_of_dms = None
    allowed_number_of_dm_follow_ups = None
    allowed_number_of_loom_follow_ups = None
    todays_sent_dms = None
    final_allowed_number_of_dms = None

    can_send_dm_today = None
    can_send_dm_follow_up_today = None
    can_send_loom_follow_up_today = None
    number_of_custom_message_commands = None
    custom_message_commands = None
    current_chunk_dm = None

    def delete_instance(self, *args, **kwargs):
        from script.models.Taggable import Taggable

        # Delete related Taggable records
        Taggable.delete().where(Taggable.taggable_id == self.id,
                                Taggable.taggable_type == 'App\\Models\\Account').execute()

        super().delete_instance(*args, **kwargs)

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

    def add_cli(self, log, print_only=False):
        from .Cli import Cli
        from .Process import Process

        log = f'[{self.username} -- {self.id}] ${log}'

        print(log)

        if print_only:
            return False

        truncated_log = (log[:254]) if log else ''

        self.log = truncated_log
        process = Process.select().where(Process.pid == os.getpid()).first()

        self.save()

        Cli.create(account=self, log=truncated_log, process=process)

    def add_screen_shot(self, cause, path):
        from .ScreenShot import ScreenShot

        max_length = 200
        truncated_cause = (cause[:max_length]) if cause else ''
        truncated_path = (path[:max_length]) if path else ''

        print('truncated_cause')
        print(truncated_cause)
        print('truncated_path')
        print(truncated_path)

        ScreenShot.create(
            account=self,
            cause=truncated_cause,
            path=truncated_path,
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

    def get_session(self):
        storage_state = self.web_session

        try:
            decoded = json.loads(storage_state)
            if isinstance(decoded, str):
                decoded = json.loads(decoded)

        except Exception as e:
            decoded = {}

        return decoded

    def should_not_post(self, command_type, hours=24):
        from .Command import Command

        n_hours_ago = hours_ago(hours)

        return Command.select().where(
            (Command.account_id == self.id) &
            (Command.type == command_type) &
            (Command.state == 'success') &
            (Command.created_at >= n_hours_ago)
        ).exists()

    def get_a_free_template(self, type):
        from .Template import Template
        from .AccountTemplate import AccountTemplate

        load_dotenv()
        random_function = fn.Random if os.getenv('DB_TYPE') == 'postgresql' else fn.Rand

        return (Template.select().where(
            (Template.type == type) &
            ~(Template.id << (AccountTemplate
                              .select(AccountTemplate.template)
                              .join(Template)
                              .where((AccountTemplate.account == self) &
                                     (Template.type == type))
                              ))
        )
                .order_by(random_function())
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
        )

    def set(self, col, value):
        setattr(self, col, value)
        self.save()

    def get_passed_days_since_creation(self):
        if not self.created_at:
            self.created_at = tehran_now()
            self.save()

        self.passed_days_since_creation = (tehran_now() - self.created_at).days

        return 1 if self.passed_days_since_creation < 1 else self.passed_days_since_creation

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

            proxy = {
                'http': 'http://paichb:yNckWHb3@207.230.104.78:29842',
                'https': 'http://paichb:yNckWHb3@207.230.104.78:29842',
            }

            response = requests.get(RequestAdapter.bulkacc_api(self.secret_key), proxies=proxy)
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

        min_hour_setting = SettingAdapter.minimum_time_for_next_login()
        max_hour_setting = SettingAdapter.maximum_time_for_next_login()

        random_hour = random.randint(min_hour_setting, max_hour_setting)

        time_delta = timedelta(seconds=random_second, minutes=random_minute, hours=random_hour)
        new_time = tehran_now() + time_delta

        self.next_login = new_time
        self.save()

        return new_time

    def next_login_has_not_reached_yet(self):
        if not self.next_login:
            return False, 0

        time_delta = max(self.next_login - tehran_now(), timedelta(0))
        return self.next_login > tehran_now(), time_delta

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
            (~(Template.id << selected_templates_subquery))
        )
                              .order_by(fn.Random())
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
            (~(Template.id << selected_templates_subquery))
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
        time_threshold = tehran_now() - timedelta(hours=hours)

        return (Command
                .select()
                .where(
            (Command.account == self) &
            (Command.type.in_(['post image', 'post video', 'post carousel'])) &
            (Command.state == 'success') &
            (Command.created_at >= time_threshold)
        )
                .exists())

    def get_number_of_successful_posts(self):
        from .Command import Command

        return (Command
                .select()
                .where(
            (Command.account == self) &
            (Command.type.in_(['post image', 'post video', 'post carousel'])) &
            (Command.state == 'success')
        )
                .count())

    def get_latest_successful_command_time(self):
        from .Command import Command

        """
        Get the latest successful post command (image, video, or carousel) post date in the format 'n hours ago'.
        """
        latest_command = (Command
                          .select()
                          .where(
            (Command.account == self) &
            (Command.type.in_(['post image', 'post video', 'post carousel'])) &
            (Command.state == 'success')
        )
                          .order_by(Command.created_at.desc())
                          .first())

        if not latest_command:
            return "No successful commands found"

        time_difference = tehran_now() - latest_command.created_at
        hours_ago = time_difference.total_seconds() // 3600

        return f"{int(hours_ago)} hours ago"

    def determine_next_post_command(self):
        """
        Determine the next post command type based on the latest post commands.
        """
        if self.sent_recent_post_command_within(random.randint(30, 40)):
            self.add_cli('We have sent a post recently')
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

    def get_profile(self):
        if self.profile:
            return self.profile

        self.assign_profile()

        return self.profile

    def assign_profile(self):

        load_dotenv()

        data = {
            'username': os.getenv('API_USERNAME'),
            'password': os.getenv('API_PASSWORD'),
            'account_id': self.id,
        }

        response = requests.post(os.getenv('ASSIGN_PROFILE_TO_ACCOUNT_API_URL'), data=data)

        return response.text

    def has_tag(self, tag_title):
        from script.models.Taggable import Taggable
        from script.models.Tag import Tag

        tag = Tag.select().where(Tag.title == tag_title).first()

        return Taggable.select().where(
            (Taggable.tag == tag) &
            (Taggable.taggable_id == self.id) &
            (Taggable.taggable_type == Taggable.get_taggable_class('Account'))
        ).exists()

    def tags(self, as_object=True):
        from script.models.Taggable import Taggable
        from script.models.Tag import Tag

        # Get all tags associated with this account
        tags = (Tag
        .select()
        .join(Taggable, on=(Taggable.tag == Tag.id))
        .where(
            (Taggable.taggable_id == self.id) &
            (Taggable.taggable_type == Taggable.get_taggable_class('Account'))
        ))

        if as_object:
            return tags

        tag_titles = [tag.title for tag in tags]
        tags = ", ".join(tag_titles)

        # Join the titles into a single string separated by commas
        return tags

    def calculate_today_dms(self):
        from script.models.Command import performed_command_count

        self.allowed_number_of_dms = calculate_daily_dms(self.get_passed_days_since_creation())
        self.todays_sent_dms = performed_command_count(self, ['dm follow up'], 24)

        count = self.allowed_number_of_dms - self.todays_sent_dms

        self.final_allowed_number_of_dms = 0 if count < 1 else count

        self.current_chunk_dm = min(get_dm_chunk(self.passed_days_since_creation), self.final_allowed_number_of_dms)

        return self.current_chunk_dm

    def get_number_of_dm_follow_ups(self):
        from .Lead import Lead

        forty_eight_hours_ago = hours_ago(48)

        self.allowed_number_of_dm_follow_ups = Lead.select().where(
            (Lead.last_state == 'dm follow up') &
            (Lead.account == self) &
            (Lead.times < 3) &
            (Lead.last_command_send_date < forty_eight_hours_ago)
        ).count()

        self.can_send_dm_follow_up_today = True if self.allowed_number_of_dm_follow_ups > 0 else False

        return self

    def get_number_of_loom_follow_ups(self):
        from .Lead import Lead
        forty_eight_hours_ago = hours_ago(48)

        self.allowed_number_of_loom_follow_ups = Lead.select().where(
            (Lead.last_state == 'loom follow up') &
            (Lead.account == self) &
            (Lead.times < 11) &
            (Lead.last_command_send_date < forty_eight_hours_ago)
        ).count()

        self.can_send_loom_follow_up_today = True if self.allowed_number_of_loom_follow_ups > 0 else False

        return self

    def get_custom_message_commands(self):
        from .Command import Command
        self.custom_message_commands = (Command.select()
        .where(
            (Command.account == self) &
            (Command.type.in_(['send loom', 'custom message'])) &
            (Command.state == 'pending')
        ))

        self.number_of_custom_message_commands = self.custom_message_commands.count()

    def pick_a_resolution(self):
        if not self.screen_resolution:
            self.screen_resolution = get_next_screen_resolution()
            self.save()

    def update_proxy_to_residential(self):
        load_dotenv()

        base = os.getenv('SERVER_URL')
        result = requests.post(base + '/account/change-profile-proxy-to-residential', {'id': self.id})

        return result.text

    class Meta:
        table_name = 'accounts'
