from .BaseAction import BaseAction
from .SearchForAction import SearchForAction
from script.extra.helper import go_to_page


class DirectlyGoToAccountPageAction(BaseAction):

    def start(self, username):
        go_to_page(self.ig, f'https://www.instagram.com/{username}/', "User")

        if self.ig.is_visible_by_text("this page isn't available") or self.ig.is_visible_by_text(
                "The link you followed may be broken, or the page may have been removed"):
            raise Exception("Sorry, this page isn't available")
