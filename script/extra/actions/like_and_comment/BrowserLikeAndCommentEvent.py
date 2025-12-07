from script.extra.helper import go_to_page
from script.models.Order import get_next_order_for_account
from script.models.OrderComment import get_next_comment_for_order, update_processing_comments
from script.extra.helper import tehran_now
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from urllib.parse import urlparse


class BrowserLikeAndCommentEvent(BaseAction):
    command = None
    comment = None
    account_age = None
    order = None

    def init(self):

        if self.ig.account.get_passed_days_since_creation() < 15:
            return self.ig.account.add_cli(f"Account is not old enough to Send comment")

        self.pick_and_mark_comment()
        self.ig.account.add_cli('Starting to comment and like ...')
        # https://www.instagram.com/reels/DRxrJa5ESf4/
        try:
            self.command = self.ig.account.create_command('comment and like', 'processing')
            self.go_to_page()
            self.ig.pause(5000, 6000)
            self.click_on_not_now()

            self.ig.pause(1000, 1200)
            self.check_fail_situations()
            self.try_like()
            self.ig.pause(1000, 1200)

            if self.comment.content:
                self.ig.page.get_by_placeholder("Add a comment…").fill(self.comment.content, timeout=3000)
                self.ig.pause(4000, 5000)
                self.ig.page.get_by_role("button", name="Post").click()

            self.take_screenshot(command_id=self.order.id)
            self.mark_comment_sent()
            self.command.update_cmd('state', 'success')
            self.ig.pause(4000, 5000)

        except LinkIsNotCorrect as e:
            # Taking screen-shot
            self.take_screenshot(command_id=self.order.id, fail_or_success='fail')

            self.ig.account.add_cli(str(e), print_only=True)
            self.order.fail('Failed to load the link')

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.take_screenshot(command_id=self.order.id, fail_or_success='fail')

            self.ig.account.add_cli(str(e), print_only=True)

            self.comment.set_status_to('free')

            if self.command:
                self.command.update_cmd('state', 'fail')

    def click_on_not_now(self):
        print('before Now now')

        if self.ig.is_visible_by_text("shared this with you") or self.ig.is_visible_by_text(
                "Stay up to date with"):

            # varinder_grewal13 shared this with you
            # Stay up to date with varinder_grewal13 by following them
            print('Not now is visible')
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
            except Exception as e:
                self.ig.account.add_cli(str(e))

        print('after Not now')
        pass

    def pick_and_mark_comment(self):
        self.order = get_next_order_for_account(self.ig.account, 'like_and_comment')

        if not self.order:
            raise Exception('There is no order')

        self.ig.account.add_cli(f'selected order: {self.order.id}', print_only=True)
        self.ig.account.add_cli(f'selected order: {self.order.target_link}', print_only=True)

        if self.order.status_is("Pending"):
            self.order.set_status_to("In progress")

        # Step 2: pick a free comment
        self.comment = get_next_comment_for_order(self.order)

        if not self.comment:

            # If we have a pending or In progress order but there's no free comment it means there's some invalid
            # processing comments in it
            self.ig.account.add_cli("There is no comment for this account updating processing ones ...",
                                    print_only=True)
            update_processing_comments(self.order)

            self.comment = get_next_comment_for_order(self.order)

            if not self.comment:
                raise Exception('There is no comment for this account')

    def go_to_page(self):

        try:
            go_to_page(self.ig, self.order.target_link, 'Post Page')
        except Exception as e:
            raise LinkIsNotCorrect(str(e))

    def check_fail_situations(self):
        # --- NEW: Check domain ---
        parsed = urlparse(self.order.target_link)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            self.order.fail("Invalid link, not an Instagram URL")
            raise Exception("Invalid link, not an Instagram URL")

            # Valid post paths: /p/{code}/ or /reel/{code}/
        path = parsed.path.strip('/').split('/')

        # Detect profile links => /username
        if len(path) == 1:
            self.order.fail("Not a valid Instagram post or reel")
            raise Exception("Not a valid Instagram post or reel")

        # Detect wrong format like /souravpalia?igsh=...
        valid_first_segment = ["p", "reel", "tv"]

        # Format A: /p/{code}
        if len(path) == 2 and path[0] in valid_first_segment:
            pass  # valid

        # Format B: /username/reel/{code}
        elif len(path) == 3 and path[1] in valid_first_segment:
            pass  # valid

        else:
            self.order.fail("Not a valid Instagram post or reel")
            raise Exception("Not a valid Instagram post or reel")

        if path[0] == 'reels':

            try:
                self.ig.page.locator("svg[aria-label='Comment']").first.click(timeout=3000)
                self.ig.pause(2000, 3000)

            except Exception as e:
                print(str(e))
                self.ig.page.locator("div[role='button']").filter(
                    has=self.ig.page.locator("svg[aria-label='Comment']")).click()

        if self.ig.is_visible_by_text('This account is private'):
            self.order.fail('Account is private')
            raise Exception('Account is private')

        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            self.order.fail('Comments on this post have been limited')
            raise Exception('Comments on this post have been limited')

        if self.ig.is_visible_by_text("Post isn't available") or self.ig.is_visible_by_text(
                "The link may be broken") or self.ig.is_visible_by_text("the profile may have been removed"):
            self.order.fail("Post isn't available")
            raise Exception("Post isn't available")

        if self.ig.is_visible_by_text("Something went wrong") or self.ig.is_visible_by_text(
                "There's an issue and the page could not be loaded"):
            self.order.fail("Something went wrong")
            raise Exception("Something went wrong")

        # locator = self.ig.page.locator('svg[aria-label="Comment"]').first
        #
        # if not locator.is_visible():
        #     self.order.fail("Comment box is not visible")
        #     raise Exception("Comment box is not visible")

    #
    def try_like(self):
        """
        Try to like post with multiple selectors
        """
        if self.is_liked():
            return False

        selectors = [
            # 'div:not([aria-label*="comment"]) div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
            'div[style*="max-width"] section div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
            'div.x1ypdohk[data-visualcompletion="ignore-dynamic"] div.x1i10hfl.x972fbf.x10w94by[role="button"]',
            'section div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
            'article div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    self.ig.pause(1000, 2000)
                    if self.is_liked():
                        return True
            except:
                continue

        return False

    def is_liked(self):
        """
        Check if post is already liked
        """
        try:
            selectors = [
                'svg[aria-label="Unlike"]',
                'div[role="button"]:has(svg[aria-label="Unlike"])',
                'svg[fill="#ed4956"]',
            ]

            for selector in selectors:
                try:
                    if self.ig.page.locator(selector).first.count() > 0:
                        if self.ig.page.locator(selector).first.is_visible():
                            return True
                except:
                    continue
            return False
        except:
            return False

    def mark_comment_sent(self):
        self.comment.set_status_to('sent')
        self.order.add_completed_count()
        self.order.make_order_completed()
