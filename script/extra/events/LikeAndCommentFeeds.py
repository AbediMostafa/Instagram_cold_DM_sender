import traceback
from .BaseActionState import BaseActionState
from script.extra.actions.LikeAndComment import LikeAndComment
from script.extra.helper import pause
import random
from script.extra.helper import chat_ai


class LikeAndCommentFeeds(BaseActionState):
    medias = None
    action = None

    likes = 0
    comments = 0

    def cant(self):
        return not self.medias or (not self.action.chunk_to_like and not self.action.chunk_to_comment)

    def init_state(self):
        self.account.add_cli("Starting to like and comment feeds ...")
        self.medias = self.ig.feeds.get('feed_items', [])
        self.action = LikeAndComment(self.account)
        self.action.calculate_number_of_actions_strategy()

    def cant_state(self):

        if not self.medias:
            text = f"We don't have any feeds to like and comment"

        if not self.action.chunk_to_like and not self.action.chunk_to_comment:
            text = f"We can't like and comment today"

        self.account.add_log(text)

        return False

    def randomly_like(self, media):
        # Chance to like the media (1/4)
        if random.randint(1, 3) == 1:

            if self.likes == self.action.chunk_to_like:
                return True

            pause(5, 11)
            self.account.add_cli(f"Liking {media['id']} ...")
            self.command = self.account.create_command('like post', 'processing')
            self.ig.media_like(media['id'])
            self.account.add_cli(f"Media been liked successfully")
            self.command.update_cmd('state', 'success')

            self.likes += 1

    def randomly_comment(self, media):
        if random.randint(1, 3) == 1:

            if self.comments == self.action.chunk_to_comment:
                return True

            pause(15, 25)
            self.account.add_cli(f"Commenting on {media['id']} ...")
            self.command = self.account.create_command('comment post', 'processing')

            caption = media.get('caption', {}).get('text', '')
            self.account.add_cli(f"medias caption: {caption}")
            prompt = f"Write a friendly and engaging comment with emojis for the following Instagram caption: \"{caption}\", make it very very short and dont overuse emojis, just give me the comment, remove extra words and single quote or double quotes"

            comment = chat_ai(prompt)
            self.account.add_cli(f"Generated comment:  {comment}")

            self.ig.media_comment(media['id'], comment)
            self.account.add_cli(f"Put a comment on media successfully")
            self.command.update_cmd('state', 'success')

            self.comments += 1


    def success_state(self):
        for media in self.medias:

            if 'media_or_ad' in media:
                media = media['media_or_ad']

                if media:
                    self.account.add_cli(f"Processing media {media['id']}")
                    self.randomly_like(media)
                    self.randomly_comment(media)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem liking or commenting: {str(e)}")
        self.account.add_log(traceback.format_exc())
