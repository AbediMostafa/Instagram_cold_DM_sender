from .BaseAction import BaseAction


class ClickOnLikesAction(BaseAction):

    def start(self):
        try:
            self.ig.page.locator("a:has-text('likes')").click(timeout=4000)

        except Exception as e:
            self.ig.page.locator("a:has-text('others')").click(timeout=4000)