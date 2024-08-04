import traceback
from .BaseActionState import BaseActionState
from script.extra.helper import pause
from script.models.Template import get_a, delete


class ChangeUsernameEvent(BaseActionState):
    attempt = 0
    username = None

    def cant(self):
        return self.account.username_changed or not self.username

    def get_username(self):
        self.username = get_a('username').text
        self.account.add_cli(f'Selected username: {self.username}')

    def init_state(self):
        self.attempt = 0
        self.account.add_cli(f"Changing {self.account.username}'s username")
        self.get_username()

    def cant_state(self):

        if self.account.username_changed:
            return self.account.add_cli(f"{self.account.username}'s username has been changed already.")

        if not self.username:
            self.account.add_cli(f"We don't have a username for : {self.account.username}")
            self.account.add_log(f"We don't have a username for : {self.account.username}")

        return False

    def delete_current_username(self):
        return delete('username', self.username)

    def try_change_username(self):
        try:
            self.attempt += 1
            self.account.add_cli(f"Trying to change the username for the {self.attempt} time ...")
            self.ig.change_username(self.username)
            self.account.add_cli('Username changed successfully')
            self.delete_current_username()

        except Exception as e:
            self.delete_current_username()
            self.account.add_cli(str(e))

            if self.attempt > 2:
                raise Exception(f'Problem changing username : {str(e)}')

            if 'user with that username already exists' in str(e) or "username isn't available" in str(
                    e) or 'Enter a name under 30 characters' in str(
                e) or "You can't end your username with a period" in str(e):
                pause(2, 4)

                self.get_username()
                self.try_change_username()

    def success_state(self):
        self.account.set_state('set username', 'app_state')
        self.command = self.account.create_command('set username', 'processing')
        self.try_change_username()
        self.command.update_cmd('state', 'success')
        self.account.set('username', self.username)
        self.account.set('username_changed', 1)

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')
        self.account.add_cli(f"Problem changing Username : {str(e)}")
        self.account.add_log(traceback.format_exc())
