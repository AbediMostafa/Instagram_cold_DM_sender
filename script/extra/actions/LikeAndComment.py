from script.models.Lead import Lead
from script.models.Command import Command
from peewee import SQL
from script.extra.adapters.SettingAdapter import SettingAdapter
import random


class LikeAndComment(object):
    chunk_to_like = None
    chunk_to_comment = None

    def __init__(self, account):
        self.account = account

    def get_a_random_lead(self):
        random_follow_command = (Command.select().where(
            (Command.type == 'follow') &
            (Command.state == 'success')
        )
                                 .order_by(SQL('RAND()'))
                                 .first())

        if random_follow_command:
            return random_follow_command.lead

        random_lead_with_instagram_id = (Lead
                                         .select()
                                         .where(~Lead.instagram_id.is_null())
                                         .order_by(SQL('RAND()'))
                                         .first())

        if random_lead_with_instagram_id:
            return random_lead_with_instagram_id

        return (Lead
                .select()
                .order_by(SQL('RAND()'))
                .first())

    def calculate_number_of_actions_strategy(self):

        allowed_likes = min(self.account.passed_days_since_creation + 1, SettingAdapter.max_like())
        allowed_comments = min(self.account.passed_days_since_creation + 1, SettingAdapter.max_comment())

        successful_likes = Command.successful_commands_within_passed_24hours(self.account, 'like post')
        successful_comments = Command.successful_commands_within_passed_24hours(self.account, 'comment post')

        self.account.add_cli(
            f"We have liked {successful_likes} posts and commented on {successful_comments} posts in the past 24 hours")

        final_like_count = allowed_likes - successful_likes
        final_comment_count = allowed_comments - successful_comments

        self.account.add_cli(f"We can finally do {final_like_count} likes and {final_comment_count} comments")

        chunk_to_like = min(final_like_count, SettingAdapter.like_chunk())
        chunk_to_comment = min(final_comment_count, SettingAdapter.comment_chunk())

        self.chunk_to_like = random.randint(1, chunk_to_like) if chunk_to_like > 0 else 0
        self.chunk_to_comment = random.randint(1, chunk_to_comment) if chunk_to_comment > 0 else 0

        self.account.add_cli(f"Chunk to like :{str(self.chunk_to_like)},Chunk to comment :{str(self.chunk_to_comment)}")
