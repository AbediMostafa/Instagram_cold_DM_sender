from .BaseAction import BaseAction
from script.extra.helper import go_to_page
from script.extra.helper import go_to_page


class GoToProfilePageAction(BaseAction):

    def start(self):
        self.ig.account.add_cli('Going to Accounts profile page')
        go_to_page(self.ig, 'https://www.instagram.com/accounts/edit/', "Edit")

        self.ig.pause(4000, 5000)

        go_to_page(self.ig, 'https://accountscenter.instagram.com/?entry_point=app_settings', "App setting")
        self.ig.pause(3000, 4500)
