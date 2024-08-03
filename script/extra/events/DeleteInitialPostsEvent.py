import traceback
from .BaseActionState import BaseActionState


class DeleteInitialPostsEvent(BaseActionState):

    def cant(self):
        return self.account.initial_posts_deleted

    def init_state(self):
        self.account.add_cli("Deleting Initial Posts ... ")

    def cant_state(self):
        return self.account.add_cli("Initial posts have been deleted before")

    def success_state(self):
        self.account.set_state('delete initial posts', 'app_state')
        self.command = self.account.create_command('delete initial posts', 'processing')
        self.ig.delete_initial_posts()
        self.command.update_cmd('state', 'success')
        self.account.set('initial_posts_deleted', 1)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem deleting initial posts : {str(e)}")
        self.account.add_log(traceback.format_exc())
