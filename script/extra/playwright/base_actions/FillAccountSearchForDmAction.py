from .BaseAction import BaseAction


class FillAccountSearchForDmAction(BaseAction):
    search_input_locator = 'input[name="queryBox"][placeholder="Search"]'

    def start(self, phrase):

        try:
            self.ig.page.get_by_placeholder("Search").press_sequentially(phrase, delay=120, timeout=7000)

        except:
            self.ig.account.add_cli('There is no locator with Search placeholder trying another method ...')
            self.ig.page.locator(self.search_input_locator).press_sequentially(phrase, delay=120, timeout=6000)
