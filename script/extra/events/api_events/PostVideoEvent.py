import traceback
from .BaseActionState import BaseActionState
from script.extra.helper import *
import random
from script.extra.instagram.api.InstagramMobile import InstagramMobile


class PostVideoEvent(BaseActionState):
    video_template = None
    image_template = None
    video_path = None
    image_path = None
    should_not_post = None
    caption = None
    tmp = None

    def cant(self):
        return self.should_not_post or not self.video_template

    def init_state(self):
        self.account.add_cli(f"Posting a video ...")
        self.should_not_post = self.account.should_not_post('post video', random.randint(20, 24))
        self.image_template, self.video_template = self.account.get_a_video()

    def cant_state(self):

        if self.should_not_post:
            return self.account.add_cli("Cant post a video today")

        if not self.video_template:
            self.account.add_cli(f"We don't have a video template for : {self.account.username}")

        return False

    def success_state(self):
        self.login()
        self.generate_path()
        self.generate_caption()

        self.account.set_state('post video', 'app_state')
        self.command = self.account.create_command('post video', 'processing')

        self.account.add_cli("Uploading the video ....")

        self.ig.video_upload(self.video_path, self.caption, self.image_path)

        self.command.update_cmd('state', 'success')

        if self.image_template:
            self.account.attach_template(self.image_template)
        self.account.attach_template(self.video_template)

    def login(self):
        self.ig = InstagramMobile(self.account)
        self.ig.log_in()

    def generate_path(self):
        self.account.add_cli("Generating path of video and thumbnail ...")

        self.tmp = generate_random_folder()

        if self.image_template:
            self.image_path = self.image_template.download_image(self.tmp)
            self.image_path = process_image(self.image_path, self.tmp)

        self.video_path = self.video_template.download_image(self.tmp)


    def generate_caption(self):
        prompt = f'rewrite this text without plagiarism please remove extra text and give me pure text:{self.video_template.caption}'
        self.caption = chat_ai(prompt)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem posting video : {str(e)}")
        self.account.add_log(traceback.format_exc())
