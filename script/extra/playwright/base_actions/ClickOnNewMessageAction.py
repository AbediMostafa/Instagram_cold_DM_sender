from .BaseAction import BaseAction
from .GoToThreadsAction import GoToThreadsAction
from .TurnOnNotificationAction import TurnOnNotificationAction

class ClickOnNewMessageAction(BaseAction):

    def start(self):

        try:
            self.ig.page.get_by_role("button", name="New message").click(timeout=3000)
        except:
            try:
                self.ig.account.add_cli('There is no New message button clicking on Send message instead ...')
                self.ig.page.get_by_role("button", name="Send message").click(timeout=3000)
            except:
                try:
                    self.ig.account.add_cli('Problem clicking on Send message going to threads to try again ...')

                    GoToThreadsAction(self.ig).start()
                    TurnOnNotificationAction(self.ig).start()

                    self.ig.page.get_by_role("button", name="Send message").click(timeout=3000)
                except:
                    self.ig.page.get_by_role("button", name="New message").click(timeout=3000)