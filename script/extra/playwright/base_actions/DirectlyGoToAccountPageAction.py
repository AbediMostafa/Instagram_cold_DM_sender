from .BaseAction import BaseAction
from .SearchForAction import SearchForAction


class DirectlyGoToAccountPageAction(BaseAction):

    def start(self, username):
        self.ig.page.goto(f'https://www.instagram.com/{username}/')

        if self.ig.is_visible_by_text("this page isn't available") or self.ig.is_visible_by_text(
                "The link you followed may be broken, or the page may have been removed"):
            raise Exception("Sorry, this page isn't available")
