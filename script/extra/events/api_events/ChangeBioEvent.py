import traceback
from .BaseActionState import BaseActionState
from script.extra.helper import chat_ai
from pathlib import Path
import os


class ChangeBioEvent(BaseActionState):
    bio = None

    def cant(self):
        return self.account.has('bio') or not self.bio

    def get_bio(self):
        prompt = """
        make me one unique bio saying that we grow ecomm brands to 50-100k months in 90 days on tiktok, 
        but use promised revenue, make it short like:
        Rule TikTok, Surge Your Ecomm Revenue ➔ www.boomboomcreatives.com
        Ignite Your Brand's TikTok Revolution for Massive Growth ➔ www.boomboomcreatives.com
        Master TikTok & Watch Your Ecomm Sales Surge ➔ www.boomboomcreatives.com
        just give me the bio and remove extra words
        """

        self.bio = chat_ai(prompt)
        self.account.add_cli(f'selected bio : {self.bio}')

    def init_state(self):
        self.account.add_cli(f"Changing {self.account.username}'s bio")
        self.get_bio()

    def cant_state(self):

        if self.account.has('bio'):
            return self.account.add_cli(f'{self.account.username} has a bio')

        if not self.bio:
            self.account.add_cli(f"We don't have a bio for : {self.account.username}")

        return False

    def success_state(self):
        self.account.set_state('set bio', 'app_state')
        self.command = self.account.create_command('set bio', 'processing')

        self.ig.change_bio(self.bio)
        self.command.update_cmd('state', 'success')
        self.account.set('bio', self.bio)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem changing bio : {str(e)}")
        self.account.add_log(traceback.format_exc())
