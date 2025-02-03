from .BaseAction import BaseAction


class GoToThreadsAction(BaseAction):

    def start(self):
        self.ig.account.add_cli('Going to threads page ...')
        try:
            self.ig.page.locator('a[aria-label*="Direct messaging"]').click(timeout=3000)

        except:
            try:
                self.ig.page.goto("https://www.instagram.com/direct/inbox/")
            except:
                try:
                    self.ig.page.locator('a[aria-label^="Direct messaging"]').first.click()
                except:
                    self.ig.page.locator('a[aria-label^="Direct messaging"]').last.click()

        self.ig.pause(4000, 6000)
        return self
