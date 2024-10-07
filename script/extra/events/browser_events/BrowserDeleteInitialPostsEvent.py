from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import random
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Template import get_a, delete


class BrowserDeleteInitialPostsEvent(InstagramMiddleware):
    base = None
    username_counter = 0
    command = 0

    def execute(self):

        if self.ig.account.initial_posts_deleted:
            return self.ig.account.add_cli(f"Initial posts have been deleted before")

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem deleting initial posts : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.ig.account.add_cli('Going to profile page')
        self.ig.page.goto(f'https://www.instagram.com/{self.ig.account.username}/')
        self.ig.pause(4000, 5000)
        self.ig.account.add_cli('We are on profile page')

        self.ig.account.set_state('delete initial posts', 'app_state')
        self.command = self.ig.account.create_command('delete initial posts', 'processing')

    def change_hook(self):

        posts = self.ig.page.locator(
            'div._ac7v.xras4av.xgc1b0m.xat24cr.xzboxd6 > div.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p.xfllauq.xo2y696.x11i5rnm.x2pgyrj')

        self.ig.account.add_cli(f'There are {posts.count()} initial posts')

        for post in posts.all():
            post.locator('a').click()
            self.ig.pause(2000, 3000)
            self.ig.page.locator('div[role="button"]:has(svg[aria-label="More options"])').click()
            self.ig.pause(2000, 3000)
            self.ig.page.locator('button:has-text("Delete")').click()
            self.ig.pause(2000, 3000)
            self.ig.page.locator('button:has-text("Delete")').click()
            self.ig.pause(3000, 4500)


    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('initial_posts_deleted', 1)
