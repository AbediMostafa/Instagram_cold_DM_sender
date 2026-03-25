from script.models.Command import performed_command_count
from script.models.Lead import Lead
from script.extra.helper import calculate_daily_dms, get_dm_chunk
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
import traceback


class BrowserGetAccountUsernameEvent:
    command = None
    username = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        self.ig.account.add_cli('Starting to get account username ...')

        self.click_on_profile()
        self.ig.pause(4000, 5000)
        self.get_username()
        self.ig.pause(4000, 5000)
        self.ig.account.add_cli(f'Username: {self.username}')
        self.ig.account.set('username', self.username)


    def click_on_profile(self):
        try:
            self.ig.page.get_by_role("link").filter(has=self.ig.page.locator('span[role="link"]')).first.click()
        except Exception as e:
            self.ig.account.add_cli('Couldnt click on Profile trying second way ...')

            try:
                self.ig.page.locator("text=Profile").first.click(timeout=4500)
            except Exception as e:
                self.ig.account.add_cli('Couldnt click on text=Profile trying third way ...')
                self.ig.page.get_by_role("link", name="Profile").click(timeout=4500)

    def get_username(self):

        try:
            locator = self.ig.page.locator('h2 span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft')
            locator.wait_for(state='visible', timeout=5000)
            self.username = locator.inner_text(timeout=3000)

            self.ig.account.add_cli(f'IG username : {self.username}')
        except:
            self.ig.account.add_cli('Couldnt get username trying second way ...')
            locator = self.ig.page.locator('h1 span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft')
            locator.wait_for(state='visible', timeout=5000)
            self.username = locator.inner_text(timeout=3000)
