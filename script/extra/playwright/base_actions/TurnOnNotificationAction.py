from script.extra.playwright.base_actions.BaseAction import BaseAction


class TurnOnNotificationAction(BaseAction):

    def start(self):
        self.ig.account.add_cli('Turn on notification...')

        try:
            self.ig.pause(2000, 3000)
            self.ig.page.get_by_role("button", name="Turn On", exact=True).click(timeout=3500)
            self.ig.pause(5000, 6000)
        except:
            self.ig.account.add_cli("Turn On doesn't exists")
            pass