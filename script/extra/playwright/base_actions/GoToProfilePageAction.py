from .BaseAction import BaseAction


class GoToProfilePageAction(BaseAction):

    def start(self):
        self.ig.account.add_cli('Going to Accounts profile page')

        self.ig.page.goto('https://www.instagram.com/accounts/edit/')
        self.ig.pause(4000, 5000)
        self.ig.page.goto("https://accountscenter.instagram.com/?entry_point=app_settings")
        self.ig.pause(3000, 4500)
