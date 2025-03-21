from .BaseAction import BaseAction


class ClickOnNextPostAction(BaseAction):

    def start(self):
        self.ig.page.locator("div._aaqg._aaqh button._abl-").first.click()
