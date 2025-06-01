from .BaseAction import BaseAction


class ClickOnFollowingAction(BaseAction):

    def start(self):
        try:
            self.ig.page.get_by_role("link", has_text="following").click(timeout=4000)

        except Exception as e:
            self.ig.account.add_cli('Problem clicking on following for the first time ... trying second method')
            self.ig.page.locator("a:has-text('following')").click(timeout=4000)
