import traceback
from .BaseActionState import BaseActionState
from script.extra.helper import *

import os
from pathlib import Path


class PostImageEvent(BaseActionState):
    image_path = None
    should_not_post = None
    caption = None

    def cant(self):
        return self.should_not_post or not self.template

    def init_state(self):
        self.should_not_post = self.account.should_not_post('post image')
        self.account.add_cli(f"Posting an image ...")
        self.template = self.account.get_a_free_template('image-post')
        self.account.add_cli(
            f"We selected : {self.template.text} post image for the : {self.account.username}")

    def cant_state(self):

        if self.should_not_post:
            return self.account.add_cli("Cant post an image today")

        if not self.template:
            self.account.add_cli(f"We don't have a post image for : {self.account.username}")
            self.account.add_log(f"We don't have a post image for : {self.account.username}")

        return False

    def generate_image(self):
        self.tmp = generate_random_folder()
        image_path = self.template.download_image(self.tmp)

        self.image_path = process_image(image_path, self.tmp)

    def generate_caption(self):
        prompt = f'rewrite this text without plagiarism please remove extra text and give me pure text:{self.template.caption}'
        self.caption = chat_ai(prompt)

    def success_state(self):
        self.generate_image()
        self.generate_caption()

        self.account.set_state('post image', 'app_state')
        self.command = self.account.create_command('post image', 'processing')

        self.ig.photo_upload(self.image_path, self.caption)

        self.command.update_cmd('state', 'success')
        self.account.attach_template(self.template)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem posting image : {str(e)}")
        self.account.add_log(traceback.format_exc())
