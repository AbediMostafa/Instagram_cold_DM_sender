from peewee import *
import json
from datetime import timedelta
from .Proxy import Proxy
from .Profile import Profile
from .Category import Category
from .Service import Service
from .Color import Color, get_next_color
from .Country import Country
import random
from dotenv import load_dotenv
import os
import requests
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from script.extra.helper import tehran_now, hours_ago, get_dm_chunk, calculate_daily_dms


class Account(BaseWithTimeZoneModel):
    proxy = ForeignKeyField(Proxy, backref='accounts', null=True)
    color = ForeignKeyField(Color, backref='accounts', null=True)
    profile = ForeignKeyField(Profile, backref='accounts', null=True)
    category = ForeignKeyField(Category, backref='accounts', null=True)
    service = ForeignKeyField(Service, backref='accounts', null=True)

    # Which country this account operates in. Used for warm-up (location/hashtag),
    # lead generation, and picking the right templates.
    country = ForeignKeyField(Country, backref='accounts', null=True)

    secret_key = CharField(null=True)
    username = CharField(unique=True)
    password = CharField()
    email_password = CharField(null=True)
    name = CharField(null=True)
    phone = CharField(null=True)
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
    api_is_used = SmallIntegerField(default=0)
    is_active = SmallIntegerField(default=1)
    is_public = SmallIntegerField(default=0)
    screenshot_taken = SmallIntegerField(default=0)
    is_verify = SmallIntegerField(default=0)
    two_factor_activated = SmallIntegerField(default=0)
    web_session = TextField(null=True)
    mobile_session = TextField(null=True)
    log = TextField(null=True)
    updated_at = DateTimeField(null=True)
    next_login = DateTimeField(null=True)

    # Upload-Post connection lifecycle: none -> pending -> connecting -> connected
    # Can also be: failed, disconnecting
    # upload_post_status = CharField(default='none')

    # The profile number assigned on Upload-Post (e.g. '001', '002').
    # Set once during connect, never reused across accounts.
    # upload_post_username = CharField(null=True)

    # These are runtime values, not stored in DB. They get calculated
    # on the fly when deciding how many DMs to send, etc.
    passed_days_since_creation = None
    allowed_number_of_dms = None
    allowed_number_of_dm_follow_ups = None
    allowed_number_of_loom_follow_ups = None
    todays_sent_dms = None
    final_allowed_number_of_dms = None

    can_send_dm_today = None
    can_send_dm_follow_up_today = None
    can_send_loom_follow_up_today = None
    number_of_custom_message_commands = 0
    custom_message_commands = None
    current_chunk_dm = None

    def delete_instance(self, *args, **kwargs):
        """Clean up polymorphic taggable records before deleting the account."""
        from script.models.Taggable import Taggable

        Taggable.delete().where(Taggable.taggable_id == self.id,
                                Taggable.taggable_type == 'App\\Models\\Account').execute()

        super().delete_instance(*args, **kwargs)

    def set_state(self, state='suspended', _type='instagram_state', log=-1):
        """Update the account's state (instagram_state or app_state) and optionally its log."""
        setattr(self, _type, state)

        if log != -1:
            self.log = log

        # Save the instance with the new state
        self.save()

    def add_warning(self, cause, duration=24):
        from .Warning import Warning
        Warning.create(account=self, cause=cause, duration=duration)

    def add_log(self, log):
        from .Log import Log
        Log.create(account=self, log=log)

    def add_cli(self, log, print_only=False):
        """
        Print a log line to stdout with the account's username and ID prefix.
        The DB write is currently disabled (returns early) to reduce write load.
        """
        from .Cli import Cli
        from .Process import Process

        log = f'[{self.username} -- {self.id}] ${log}'
        print(log)
        return False

        truncated_log = (log[:254]) if log else ''
        Cli.create(account=self, log=truncated_log)

    def add_screen_shot(self, cause, path):
        from .ScreenShot import ScreenShot

        max_length = 200
        truncated_cause = (cause[:max_length]) if cause else ''
        truncated_path = (path[:max_length]) if path else ''

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
        """Parse and return the stored web session. Handles double-encoded JSON gracefully."""
        storage_state = self.web_session

        try:
            decoded = json.loads(storage_state)
            if isinstance(decoded, str):
                decoded = json.loads(decoded)
        except Exception as e:
            decoded = {}

        return decoded

    def should_not_post(self, command_type, hours=24):
        """Check if a successful command of this type was already sent within the last N hours."""
        from .Command import Command

        n_hours_ago = hours_ago(hours)

        return Command.select().where(
            (Command.account_id == self.id) &
            (Command.type == command_type) &
            (Command.state == 'success') &
            (Command.created_at >= n_hours_ago)
        ).exists()

    def get_a_free_template(self, type):
        """
        Get a random template of the given type that this account hasn't used yet.
        The account_template pivot table tracks which templates have been consumed.
        """
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

    def attach_template(self, template, url=None):
        """
        Mark a template as posted by this account.
        Creates an account_template row in the 'completed' state with the
        public URL of the post (when known). created_at is set to now and
        acts as the post timestamp (the table has no separate posted_at).

        Used by the non-custom flow where no record existed beforehand.
        The custom flow uses the row claimed by get_pending_custom_template
        instead and updates it directly.
        """
        from .AccountTemplate import AccountTemplate

        now = tehran_now()

        return AccountTemplate.create(
            account=self,
            template=template,
            status='completed',
            url=url,
            created_at=now,
            updated_at=now,
        )

    def get_pending_custom_template(self):
        """
        Atomically claim one pending custom-template assignment for this
        account and flip it to 'processing'. The corresponding template
        must be marked is_custom=true and have a supported type.

        Returns (template, account_template_record) on success, or
        (None, None) when nothing is available. The template type can
        be inspected via template.type.

        Atomicity is enforced the same way as get_next_account in
        AccountHelper: select candidate ids, then update WHERE status
        is still 'pending' and check the affected row count.
        """
        from .AccountTemplate import AccountTemplate
        from .Template import Template

        supported_types = ['image-post', 'video-post', 'carousel']

        candidates = list(
            AccountTemplate
            .select(AccountTemplate.id)
            .join(Template)
            .where(
                (AccountTemplate.account == self) &
                (AccountTemplate.status == 'pending') &
                (Template.is_custom == True) &
                (Template.type.in_(supported_types))
            )
            .order_by(AccountTemplate.id)
            .limit(5)
        )

        if not candidates:
            return None, None

        now = tehran_now()

        for candidate in candidates:
            updated = (
                AccountTemplate
                .update(status='processing', updated_at=now)
                .where(
                    (AccountTemplate.id == candidate.id) &
                    (AccountTemplate.status == 'pending')
                )
                .execute()
            )

            if updated > 0:
                at_record = AccountTemplate.get_by_id(candidate.id)
                template = Template.get_by_id(at_record.template_id)
                return template, at_record

        return None, None

    def create_command(self, _type, state, lead=None, times=0, category=None):
        from .Command import Command

        return Command.create(
            account=self,
            type=_type,
            state=state,
            lead=lead,
            times=times,
            category=category,
        )

    def set(self, col, value):
        setattr(self, col, value)
        self.save()

    def get_passed_days_since_creation(self):
        if not self.created_at:
            self.created_at = tehran_now()
            self.save()

        self.passed_days_since_creation = (tehran_now() - self.created_at).days

        return 1 if self.passed_days_since_creation < 1 else int(self.passed_days_since_creation)

    def get_proxy(self):
        from .AccountHelper import get_first_proxy_with_less_accounts

        if self.proxy:
            return self.proxy

        self.proxy = get_first_proxy_with_less_accounts()

        if not self.proxy:
            raise Exception('No Proxy left, try to add more')

        return self.proxy

    def get_verification_code(self, secret_key=None):
        if not self.secret_key:
            return ""

        import pyotp
        s_key = secret_key or self.secret_key
        clean_secret = s_key.replace(" ", "")

        totp = pyotp.TOTP(clean_secret)

        return totp.now()

    def add_direct(self, text, lead, direct, sender='account', type='text'):
        """Save a DM to the database, creating a thread if one doesn't exist yet."""
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
        """Same as add_direct but uses thread_url_id instead of thread_id from the API."""
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
        """
        Set next_login to a random time in the future. The random range comes
        from settings so we can tune how often accounts wake up.
        """
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
        """Check if it's too early to log in again. Returns (bool, remaining timedelta)."""
        if not self.next_login:
            return False, 0

        time_delta = max(self.next_login - tehran_now(), timedelta(0))
        return self.next_login > tehran_now(), time_delta

    def get_color(self):
        """Get the account's color, assigning one if it doesn't have one yet."""
        if not self.color:
            self.color = get_next_color()
            self.save()

        if self.color:
            self.add_cli(f"Account's color : {self.color.title}")
            return self.color

        return None

    def get_a_carousel(self):
        """
        Pick a carousel set that this account hasn't used yet, matching the account's color.
        Returns all slides in that carousel ordered by uid, or None if nothing is available.
        """
        from .AccountTemplate import AccountTemplate
        from .Template import Template

        selected_templates_subquery = (AccountTemplate
                                       .select(AccountTemplate.template)
                                       .where(AccountTemplate.account == self))

        available_carousel = (Template
                              .select()
                              .where(
            (Template.type == 'carousel') &
            (Template.color == self.get_color()) &
            (~(Template.id << selected_templates_subquery))
        )
                              .order_by(fn.Random())
                              .first())

        return (Template
                .select()
                .where(Template.carousel_id == available_carousel.carousel_id)
                .order_by(Template.uid)) if available_carousel else None

    def get_a_video(self):
        """
        Pick a video post that this account hasn't used yet. Video posts come in pairs:
        a video file and a cover image, linked by carousel_id.
        Returns (image_template, video_template) or (None, None).
        """
        from .AccountTemplate import AccountTemplate
        from .Template import Template

        selected_templates_subquery = (AccountTemplate
                                       .select(AccountTemplate.template)
                                       .where(AccountTemplate.account == self))

        video_template = ((Template
        .select()
        .where(
            (Template.type == 'video-post') &
            (Template.sub_type == 'video') &
            (~(Template.id << selected_templates_subquery))
        ))
                          .order_by(fn.Random())
                          .first())

        if not video_template:
            return None, None

        image_template = (Template
                          .select()
                          .where(
            (Template.carousel_id == video_template.carousel_id) &
            (Template.sub_type == 'image') &
            (Template.type == 'video-post')
        )
                          .first())

        return image_template, video_template,

    def get_latest_post_commands(self, limit=3):
        """Fetch the most recent successful post commands (image, video, carousel)."""
        from .Command import Command

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
        """True if any successful post was made within the last N hours."""
        from .Command import Command

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

    def get_post_action(self):
        next_command = self.determine_next_post_command()
        return self.execute_posting(next_command)

    def execute_posting(self, next_command):
        from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
        from script.extra.events.browser_events.BrowserPostVideoEvent import BrowserPostVideoEvent
        from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent

        types = {
            'post carousel': BrowserPostCarouselEvent,
            'post video': BrowserPostVideoEvent,
            'post image': BrowserPostImageEvent,
        }

        return types[next_command], next_command

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
        """Returns something like '14 hours ago' for the most recent successful post."""
        from .Command import Command

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
        Decide what type of post to upload next. We rotate between carousel, video
        and image. If a post was already uploaded recently, raise an exception.
        """
        from script.extra.exceptions import UploadedPostRecently

        if self.sent_recent_post_command_within(random.randint(24, 30)):
            raise UploadedPostRecently('We have sent a post recently')

        latest_commands = self.get_latest_post_commands(1)

        if not latest_commands:
            return 'post video'

        latest_command_types = [cmd.type for cmd in latest_commands]

        if latest_command_types[0] == 'post carousel':
            return 'post video'

        if latest_command_types[0] == 'post video':
            return 'post image'

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

        return tags

    def calculate_today_dms(self):
        """Figure out how many DMs this account is allowed to send today based on its age."""
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

    def update_proxy_to_residential(self):
        load_dotenv()

        base = os.getenv('SERVER_URL')
        result = requests.post(base + '/account/change-profile-proxy-to-residential', {'id': self.id})

        return result.text

    class Meta:
        table_name = 'accounts'