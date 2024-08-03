import traceback
from .BaseActionState import BaseActionState
from script.extra.helper import get_post_path


class PostVideoEvent(BaseActionState):
    post_video = None
    video_path = None
    should_not_post = None

    def cant(self):
        return self.should_not_post or not self.template

    def init_state(self):
        self.should_not_post = self.account.should_not_post('post video')
        self.account.add_cli(f"Posting a video ...")
        self.template = self.account.get_a_free_template('video-post')

    def cant_state(self):

        if self.should_not_post:
            return self.account.add_cli("Cant post a video today")

        if not self.template:
            self.account.add_cli(f"We don't have a video template for : {self.account.username}")
            self.account.add_log(f"We don't have a video template for : {self.account.username}")

        return False

    def success_state(self):
        self.video_path = get_post_path(self.template.text)
        self.account.add_cli(
            f"We selected : {self.template.text} post video for the : {self.account.username}")

        self.account.set_state('post video', 'app_state')
        self.command = self.account.create_command('post video', 'processing')

        self.ig.video_upload(self.video_path, self.template.caption)

        self.command.update_cmd('state', 'success')
        self.account.attach_template(self.template)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem posting video : {str(e)}")
        self.account.add_log(traceback.format_exc())
