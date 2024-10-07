import traceback
from .BaseActionState import BaseActionState


class ChangeNameEvent(BaseActionState):
    name = "Edward Air"

    def cant(self):
        return self.account.has('name')

    def init_state(self):
        self.account.add_cli(f"Changing {self.account.username}'s name")

    def cant_state(self):
        if self.account.has('name'):
            return self.account.add_cli(f"{self.account.username} has a name already.")

    def success_state(self):
        self.account.set_state('set name', 'app_state')
        self.command = self.account.create_command('set name', 'processing')
        self.ig.change_name(self.name)
        self.account.add_cli(f"Changed name successfully")
        self.command.update_cmd('state', 'success')
        self.account.set('name', self.name)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem changing name : {str(e)}")
        self.account.add_log(traceback.format_exc())
