from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
import random


class BrowserScrollAndLikeEvent(InstagramMiddleware):
    """
    Event class for executing email registration on Instagram
    """
    command = None

    def init(self):
        """
        Initialize and execute the email registration process
        """
        try:
            self.command = self.ig.account.create_command('scroll and like', 'processing')
            self.ig.account.add_cli("Starting scroll and like ...")
            go_to_page(self.ig, "https://www.instagram.com/", "Home")
            self.scroll_and_like()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback

            self.command.update_cmd('state', 'fail')
            self.ig.account.add_log(traceback.format_exc())
            self.ig.account.add_cli(f"Scroll and like failed: {str(e)}")

    def scroll_and_like(self):

        for i in range(random.randint(9, 14)):
            self.ig.page.mouse.wheel(0, random.randint(450, 650))
            self.ig.pause(2000, 4000)
            self.try_like()

    def try_like(self):

        import random

        # 60% chance to like
        if random.random() > 0.5:
            return False

        selectors = [
            # 'div:not([aria-label*="comment"]) div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
            'div[style*="max-width"] section div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
            # 'div.x1ypdohk[data-visualcompletion="ignore-dynamic"] div.x1i10hfl.x972fbf.x10w94by[role="button"]',
            # 'section div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
            # 'article div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    self.ig.pause(1000, 2000)
            except:
                continue

        return False
