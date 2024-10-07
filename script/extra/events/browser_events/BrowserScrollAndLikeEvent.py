from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
import random


class BrowserScrollAndLikeEvent(InstagramMiddleware):

    def execute(self):
        self.base.go_to_home()
        self.scroll_and_like()

    def scroll_and_like(self):

        for i in range(random.randint(10, 22)):
            self.ig.account.add_cli(f'Scroll down for the {i} time ...')
            self.ig.page.mouse.wheel(0, random.randint(450, 650))
            self.ig.pause(2000, 4000)

