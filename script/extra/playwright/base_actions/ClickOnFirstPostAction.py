from .BaseAction import BaseAction


class ClickOnFirstPostAction(BaseAction):

    def start(self):
        self.ig.page.locator("a[href^='/p/']").first.click()

