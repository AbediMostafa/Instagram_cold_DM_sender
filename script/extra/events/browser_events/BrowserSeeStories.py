from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import random


class BrowserSeeStories(InstagramMiddleware):
    first_story_locator1 = "button[aria-label^='Story by ']"
    first_story_locator2 = "button.x6s0dn4.xamitd3.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x1ypdohk.x78zum5.xdt5ytf.x18d9i69.xexx8yu.x2b8uid.x1fu8urw"
    first_story_locator3 = 'button[role="menuitem"]'

    close_story_locator1 = 'button[aria-label^=]'

    def execute(self):
        self.ig.account.add_cli('Starting to see stories ...')
        self.base.go_to_home()
        self.ig.suspect_automate_behavior_handler()

        try:
            self.click_on_first_story()
        except Exception as e:
            self.ig.account.add_cli(f'Problem seeing stories: {str(e)}')
            return False

        self.ig.pause(30000, 35000)
        self.close_the_stories()

    def click_on_first_story(self):

        try:
            self.ig.page.locator(self.first_story_locator1).first.click(timeout=3000)
        except:

            self.ig.account.add_cli('Problem clicking on first story with first locator ...')

            try:
                self.ig.page.locator(self.first_story_locator2).first.click(timeout=3000)

            except:
                self.ig.account.add_cli('Problem clicking on first story with second locator ...')
                self.ig.page.locator(self.first_story_locator3).first.click(timeout=3000)

    def close_the_stories(self):
        try:
            self.ig.page.get_by_role("button", name="Close").first.click()
        except Exception as e:
            self.base.go_to_home()
        self.ig.account.add_cli('Story closed')


