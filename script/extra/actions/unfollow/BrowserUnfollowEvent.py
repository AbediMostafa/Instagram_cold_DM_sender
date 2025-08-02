from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.base_actions.ClickOnFollowingAction import ClickOnFollowingAction
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
from script.models.Setting import Setting


class BrowserUnfollowEvent:
    command = None
    follow_scroll_element = 'div.x6nl9eh.x1a5l9x9.x7vuprf.x1mg3h75.x1lliihq.x1iyjqo2.xs83m0k.xz65tgg.x1rife3k.x1n2onr6'

    def __init__(self, ig):
        self.ig = ig
        self.category_model = self.ig.account.category

    def init(self):
        self.ig.account.add_cli('Starting unfollow...')
        DirectlyGoToAccountPageAction(self.ig).start(self.ig.account.username)
        self.ig.pause(4000, 4500)

        ClickOnFollowingAction(self.ig).start()
        self.ig.pause(4000, 4500)

        for _ in range(14):
            ScrollAction(self.ig).start(self.follow_scroll_element, 400, 700, 2000, 2500)

        self.unfollow()

    def unfollow(self):
        allowed_unfollow = int(Setting.get_value('Number of daily unfollow', 15))
        unfollowed = 0

        while unfollowed < allowed_unfollow:
            buttons = self.ig.page.query_selector_all('button:has-text("Following")')

            self.ig.account.add_cli(f"follow buttons count : {len(buttons)}")

            if not buttons:
                self.ig.account.add_cli("No more buttons found")
                break

            buttons = list(reversed(buttons))

            for button in buttons:
                try:
                    self.command = self.ig.account.create_command(
                        'unfollow',
                        'processing',
                        category=self.category_model)

                    button.click()
                    self.ig.page.wait_for_selector('text=Unfollow', timeout=3000)
                    self.ig.pause(2000, 2500)
                    self.ig.page.click('button:has-text("Unfollow")')

                    unfollowed += 1

                    self.command.update_cmd('state', 'success')

                    if unfollowed >= allowed_unfollow:
                        break

                    self.ig.account.add_cli(f'Unfollowed: {unfollowed}')
                    self.ig.pause(4000, 4500)

                except Exception as e:
                    import traceback

                    if self.command:
                        self.command.update_cmd('state', 'fail')

                    self.ig.account.add_cli(f"Problem performing unfollow : {str(e)}")
                    self.ig.account.add_log(traceback.format_exc())

            ScrollAction(self.ig).start()
