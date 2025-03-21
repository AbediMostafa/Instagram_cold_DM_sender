from .BaseAction import BaseAction
from .SearchForAction import SearchForAction
import re


class AllowCookiesAction(BaseAction):

    def start(self):
        if self.ig.is_visible_by_text("Allow the use of cookies") or self.ig.is_visible_by_text(
                "Allow all cookies") or self.ig.is_visible_by_text("Allow All Cookies"):

            try:
                self.ig.page.locator('button', has_text='Allow all cookies').click(timeout=3000)
            except:
                self.ig.page.get_by_role("button", name=re.compile(r"Allow all cookies", re.IGNORECASE)).click()

            self.ig.pause(4000, 6000)
