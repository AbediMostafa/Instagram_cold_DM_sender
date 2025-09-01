from script.extra.playwright.base_actions.SearchForAction import SearchForAction
import random
from script.extra.helper import go_to_page


class BrowserGetContactInformationEvent:
    command = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        self.ig.account.add_cli('Getting accounts phone ...')
        self.command = self.ig.account.create_command('set phone', 'processing')


        try:
            go_to_page(self.ig, 'https://accountscenter.instagram.com/personal_info/', "Personal info")

            self.ig.pause(5000, 6000)
            phone = self.ig.page.locator("div.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.x193iq5w.xeuugli").nth(1).inner_text()
            self.ig.account.add_cli(f'Founded phone : {phone}')

            self.command.update_cmd('state', 'success')
            self.ig.account.set('phone', phone)

            self.ig.account.add_cli('Account phone Got successfully!')

        except Exception as e:
            import traceback

            self.ig.account.add_cli(f"Problem Getting phone number : {str(e)}")
            if self.command:
                self.command.update_cmd('state', 'fail')

            self.ig.account.add_log(traceback.format_exc())

        finally:
            go_to_page(self.ig, 'https://www.instagram.com/', "Home")


            self.ig.pause(3000, 4000)

