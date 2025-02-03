from .BaseAction import BaseAction


class ClickOnChatAction(BaseAction):

    def start(self):
        try:
            self.ig.page.get_by_role("button", name="Chat").click(timeout=3000)

        except:
            self.ig.account.add_cli('There is no Chat button ')
