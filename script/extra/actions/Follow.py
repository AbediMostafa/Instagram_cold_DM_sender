from script.extra.adapters.SettingAdapter import SettingAdapter
import random
from script.models.Command import Command
from script.models.Lead import Lead
from datetime import datetime, timedelta
from peewee import fn,SQL


class Follow:
    account = None
    can_follow_today = None
    chunk_follow = None

    def __init__(self, account):
        self.account = account

    def number_of_follow_strategy(self):

        allowed_follow = min(self.account.passed_days_since_creation+1, SettingAdapter.max_follow())

        self.account.add_cli(f"Today's max allowed follow: {allowed_follow}")

        return allowed_follow

    def already_followed_within_passed_24hours(self):
        twenty_hours_ago = datetime.now() - timedelta(hours=24)

        followed = (Command
                    .select(fn.COUNT(Command.id).alias('count'))
                    .where(
            (Command.account == self.account) &
            (Command.type == 'follow') &
            (Command.state == 'success') &
            (Command.created_at >= twenty_hours_ago)
        )
                    .scalar())

        self.account.add_cli(f"We have followed {followed} in the past 24 hours")

        return followed

    def calculate_today_follows(self):
        count = self.number_of_follow_strategy() - self.already_followed_within_passed_24hours()

        self.can_follow_today = 0 if count < 1 else count
        self.account.add_cli(f"We can finally follow {self.can_follow_today} leads today")

        if self.can_follow_today:
            self.chunk_follow = min(self.can_follow_today, SettingAdapter.follow_chunk())

            self.chunk_follow = random.randint(1, self.chunk_follow)
            self.account.add_cli(f"Chunk to follow {self.chunk_follow}")

            return self.chunk_follow

        return self.can_follow_today

    def leads_to_follow(self):
        already_followed = Command.select(Command.lead).where(
            (Command.account == self.account) & (Command.type == 'follow') & (Command.state == 'success')
        )

        # First get leads that don't have account
        leads = (Lead.select()
                 .where(~Lead.id.in_(already_followed))
                 .where(Lead.account.is_null())
                 .order_by(SQL('RAND()'))
                 .limit(self.chunk_follow))

        # If we don't have any leads with that condition get leads with any account
        if not leads.count():
            leads = (Lead.select()
                     .where(~Lead.id.in_(already_followed))
                     .order_by(SQL('RAND()'))
                     .limit(self.chunk_follow))

        return leads
