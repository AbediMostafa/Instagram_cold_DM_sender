import traceback
from .BaseActionState import BaseActionState
from script.extra.actions.LikeAndComment import LikeAndComment
from script.extra.helper import pause
import random
from script.extra.helper import chat_ai


class LikeAndCommentLeadsPosts(BaseActionState):
    medias = None
    lead = None
    action = None
    likes = 0
    comments = 0

    def cant(self):
        return not self.lead

    def init_state(self):
        self.account.add_cli("Starting to like and comment")
        self.action = LikeAndComment(self.account)
        self.lead = self.action.get_a_random_lead()
        self.action.calculate_number_of_actions_strategy()

    def cant_state(self):
        text = f"We don't have any lead to like and follow it's posts"
        self.account.add_cli(text)
        self.account.add_log(text)

        return False

    def get_lead_instagram_id(self):
        try:
            self.get_lead_id(self.lead)
        except Exception as e:
            self.account.add_cli(f"Problem getting lead's id : {str(e)}")
            self.account.add_log(traceback.format_exc())

        pause(3, 5)

    def randomly_like(self, media):
        # Chance to like the media (1/4)
        if random.randint(1, 3) == 1:

            if self.likes == self.action.chunk_to_like:
                return True

            pause(3, 8)
            self.account.add_cli(f"Liking {media.id} ...")
            self.command = self.account.create_command('like post', 'processing', self.lead)
            self.ig.media_like(media.id)
            self.account.add_cli(f"Media been liked successfully")
            self.command.update_cmd('state', 'success')

            self.likes += 1

    def randomly_comment(self, media):
        if random.randint(1, 3) == 1:

            if self.comments == self.action.chunk_to_comment:
                return True

            pause(15, 25)
            self.account.add_cli(f"Commenting on {media.id} ...")
            self.command = self.account.create_command('comment post', 'processing', self.lead)

            caption = media.caption_text or ""
            self.account.add_cli(f"medias caption: {caption}")
            prompt = f"Write a friendly and engaging comment with emojis for the following Instagram caption: \"{caption}\", make it very very short and dont overuse emojis, just give me the comment, remove extra words and single quote or double quotes"

            comment = chat_ai(prompt)
            self.account.add_cli(f"Generated comment:  {comment}")

            self.ig.media_comment(media.id, comment)
            self.account.add_cli(f"Put a comment on media successfully")
            self.command.update_cmd('state', 'success')

            self.comments += 1

    def success_state(self):
        self.get_lead_instagram_id()

        self.medias = self.ig.user_medias(self.lead.instagram_id, 8)

        if not self.medias:
            self.account.add_cli('Selected lead dont has any media')
            return True

        for media in self.medias:
            self.account.add_cli(f"Processing media {media.id}")
            self.randomly_like(media)
            self.randomly_comment(media)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem liking or commenting: {str(e)}")
        self.account.add_log(traceback.format_exc())
