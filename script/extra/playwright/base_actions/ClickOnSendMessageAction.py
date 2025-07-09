from .BaseAction import BaseAction
from .GoToThreadsAction import GoToThreadsAction
from .TurnOnNotificationAction import TurnOnNotificationAction


class ClickOnSendMessageAction(BaseAction):

    def start(self):

        try:
            self.ig.page.get_by_role("button", name="Message", exact=True).first.click(timeout=3000)
        except:
            try:
                self.ig.page.get_by_role("button", name="Options").click()
                self.ig.pause(2500, 3500)
                self.ig.page.get_by_role("button", name="Send message").click(timeout=3000)
            except:
                raise Exception("There's not Message button in lead's page.")
