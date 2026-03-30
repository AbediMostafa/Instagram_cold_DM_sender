from script.extra.playwright.base_actions.GetPostsAction import GetPostsAction
from script.extra.exceptions import ThereIsNoPost
from script.extra.helper import go_to_page


class BrowserDeleteInitialPostsEvent:
    command = None

    def __init__(self, ig):
        self.ig = ig
        self.category_model = self.ig.account.category

    def init(self):
        self.ig.account.add_cli('Deleting initial posts...')

        try:
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except ThereIsNoPost as e:
            self.ig.account.add_cli("We caught the initial post deleted ...")
            self.ig.account.set('initial_posts_deleted', 1)
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem deleting initial posts : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.ig.account.set_state('delete initial posts', 'app_state')
        self.command = self.ig.account.create_command('delete initial posts', 'processing')
        go_to_page(self.ig, f'https://www.instagram.com/{self.ig.account.username}/', "User page")

        self.ig.pause(4000, 5000)

    def change_hook(self):
        posts = GetPostsAction(self.ig).start()

        count = min(posts.count(), 12)

        for _ in range(count):
            post = posts.first
            post.locator('a').click(timeout=3000)
            self.ig.pause(2000, 3000)
            self.ig.page.locator('div[role="button"]:has(svg[aria-label="More options"])').click(timeout=3000)
            self.ig.pause(2000, 3000)
            self.ig.page.locator('button:has-text("Delete")').click(timeout=3000)
            self.ig.pause(2000, 3000)
            self.ig.page.locator('button:has-text("Delete")').click(timeout=3000)
            self.ig.pause(6000, 7500)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('initial_posts_deleted', 1)

