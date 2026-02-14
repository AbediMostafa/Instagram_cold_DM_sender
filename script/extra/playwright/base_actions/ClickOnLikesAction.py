from .BaseAction import BaseAction
import re

class ClickOnLikesAction(BaseAction):

    def start(self):


        try:
            self.ig.page.get_by_role('button', name=re.compile(r'\d+\s+likes')).click(timeout=4000)

            # self.ig.page.get_by_role('button', name='likes').click(timeout=4000)
            # self.ig.page.locator('div[role="button"]:has-text("likes")').click(timeout=4000)
            # self.ig.page.locator("a:has-text('likes')").click(timeout=4000)

        except Exception as e:
            self.ig.account.add_cli("Problem clicking on likes: " + str(e))

            self.ig.page.locator('div[role="button"]:has-text("others")').click(timeout=4000)
            # self.ig.page.locator("a:has-text('others')").click(timeout=4000)