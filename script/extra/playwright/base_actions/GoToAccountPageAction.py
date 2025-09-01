from .BaseAction import BaseAction
from .SearchForAction import SearchForAction
from script.extra.helper import go_to_page


class GoToAccountPageAction(BaseAction):

    def start(self, phrase):
        try:
            SearchForAction(self.ig).start(phrase)
            self.ig.pause(4000, 5500)

            self.ig.page.locator(f'a[href*="/{phrase}/"]').first.click(timeout=3000)

        except:
            self.ig.account.add_cli('Problem clicking on Lead button trying url instead')
            go_to_page(self.ig, f'https://www.instagram.com/{phrase}/', "Account")
