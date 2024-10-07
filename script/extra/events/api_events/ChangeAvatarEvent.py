import traceback
from .BaseActionState import BaseActionState
import shutil

from script.extra.helper import *


class ChangeAvatarEvent(BaseActionState):

    def cant(self):
        return self.account.avatar_changed or not self.template

    def init_state(self):
        self.account.add_cli(f"Changing {self.account.username}'s avatar")
        self.template = self.account.get_a_free_template('avatar')

    def cant_state(self):
        if self.account.avatar_changed:
            return self.account.add_cli(f"{self.account.username}'s avatar has been changed already")

        if not self.template:
            self.account.add_cli(f"We don't have an avatar for : {self.account.username}")
            self.account.add_log(f"We don't have an avatar for : {self.account.username}")

        return False

    def success_state(self):
        self.account.add_cli(
            f"We selected : {self.template.text} avatar for the : {self.account.username}")
        self.account.set_state('set avatar', 'app_state')
        self.command = self.account.create_command('set avatar', 'processing')

        self.tmp = generate_random_folder()
        image_path = self.template.download_image(self.tmp)

        self.ig.change_avatar(process_image(image_path, self.tmp))

        self.command.update_cmd('state', 'success')
        self.account.set('avatar_changed', 1)
        self.account.attach_template(self.template)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem uploading avatar : {str(e)}")
        self.account.add_log(traceback.format_exc())
