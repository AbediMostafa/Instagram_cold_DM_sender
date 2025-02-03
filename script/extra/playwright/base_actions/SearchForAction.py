from .BaseAction import BaseAction


class SearchForAction(BaseAction):

    def start(self, phrase):
        try:
            search_button = self.ig.page.get_by_role("link", name="Search Search")
            search_button.wait_for(timeout=3000)
            search_button.click(timeout=3000)

        except:
            self.ig.page.get_by_role("link", name="Search").click(timeout=3000)

        self.ig.pause(3000, 3500)

        try:
            self.ig.page.get_by_placeholder("Search").fill(phrase)
        except:
            self.ig.page.locator("input[aria-label='Search input']").first.fill(phrase)
