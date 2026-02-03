from script.extra.helper import go_to_page
from script.models.Order import get_next_order_for_account
from script.models.OrderComment import get_next_comment_for_order
from script.extra.helper import tehran_now
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from urllib.parse import urlparse
from script.extra.routes import order_there_is_no_comment


class BrowserLikeAndCommentEvent(BaseAction):
    command = None
    comment = None
    account_age = None
    order = None

    def init(self):

        if self.ig.account.get_passed_days_since_creation() < 2:
            return self.ig.account.add_cli(f"Account is not old enough to Send comment")

        self.pick_and_mark_comment()
        self.ig.account.add_cli('Starting to comment and like ...')
        try:
            self.command = self.ig.account.create_command('comment and like', 'processing')
            self.post_url_validation()
            go_to_page(self.ig, self.order.target_link, 'Post Page')
            self.ig.pause(5000, 6000)
            self.click_on_not_now()

            self.ig.pause(1000, 1200)
            self.check_fail_situations()
            self.try_like()
            self.ig.pause(1000, 1200)

            if 'reels' in self.ig.page.url:
                self.ig.account.add_cli('THIS IS A REELS PAGE')

                try:
                    self.ig.page.locator("svg[aria-label='Comment']").first.click(timeout=3000)
                    self.ig.pause(3000, 3500)

                except Exception as e:
                    print(str(e))
                    self.ig.page.locator("div[role='button']").filter(
                        has=self.ig.page.locator("svg[aria-label='Comment']")).click()

            if self.comment.content:
                # self.ig.page.locator("textarea.x1i0vuye.xgcd1z6.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x5n08af.x78zum5.x1iyjqo2.x1qlqyl8.x1d6elog.xlk1fp6.x1a2a7pz.xexx8yu.xyri2b.x18d9i69.x1c1uobl.xtt52l0.xnalus7.xs3hnx8.x1bq4at4.xaqnwrm").fill(self.comment.content, timeout=3000)
                self.ig.page.get_by_placeholder("Add a comment…").fill(self.comment.content, timeout=3000)
                self.ig.pause(1500, 2000)
                self.ig.page.get_by_role("button", name="Post", exact=True).click()
                self.ig.pause(1000, 1200)

                if self.ig.is_visible_by_text("Couldn't post comment"):
                    raise LinkIsNotCorrect("Couldn't post comment")

            # self.take_screenshot(command_id=self.order.id)
            self.mark_comment_sent()
            self.command.update_cmd('state', 'success')
            self.ig.pause(3500, 4500)

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
            self.ig.account.add_cli("There is no comment for this account", print_only=True)
            order_there_is_no_comment(self.order.id)
            return self.pick_and_mark_comment()

        return self.comment

    def post_url_validation(self):
        parsed = urlparse(self.order.target_link)

        self.ig.account.add_cli("Checking if is instagram page", print_only=True)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            self.order.fail("Invalid link, not an Instagram URL")
            raise Exception("Invalid link, not an Instagram URL")

            # Valid post paths: /p/{code}/ or /reel/{code}/
        path = parsed.path.strip('/').split('/')

        self.ig.account.add_cli("Checking if is a valid url", print_only=True)
        # Detect profile links => /username
        if len(path) == 1:
            self.order.fail("Not a valid Instagram post or reel")
            raise Exception("Not a valid Instagram post or reel")

        # Detect wrong format like /souravpalia?igsh=...
        valid_first_segment = ["p", "reel", "tv"]

        self.ig.account.add_cli("Checking if is a valid post", print_only=True)
        # Format A: /p/{code}
        if len(path) == 2 and path[0] in valid_first_segment:
            pass  # valid

        # Format B: /username/reel/{code}
        elif len(path) == 3 and path[1] in valid_first_segment:
            pass  # valid

        else:
            self.order.fail("Not a valid Instagram post or reel")
            raise Exception("Not a valid Instagram post or reel")

    def check_fail_situations(self):
        # --- NEW: Check domain ---
        self.ig.account.add_cli("Checking if account is private", print_only=True)
        if self.ig.is_visible_by_text('This account is private'):
            self.order.fail('Account is private')
            raise Exception('Account is private')

        self.ig.account.add_cli("Checking if comment is limited", print_only=True)
        if self.ig.is_visible_by_text('Comments on this post have been limited'):
            self.order.fail('Comments on this post have been limited')
            raise Exception('Comments on this post have been limited')

        if self.ig.is_visible_by_text("Post isn't available") or self.ig.is_visible_by_text(
                "The link may be broken") or self.ig.is_visible_by_text("the profile may have been removed"):
            self.order.fail("Post isn't available")
            raise Exception("Post isn't available")

        self.ig.account.add_cli("Checking if There's an issue", print_only=True)
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            self.order.fail("Something went wrong")
            raise Exception("Something went wrong")

        comment_locator = self.ig.page.locator('svg[aria-label="Comment"]').first
        like_locator = self.ig.page.locator('svg[aria-label="Like"]').first

        self.ig.account.add_cli("we have a comment box", print_only=True)
        if like_locator.is_visible() and not comment_locator.is_visible():
            self.order.fail("Comment box is not visible")
            raise Exception("Comment box is not visible")

        self.ig.account.add_cli("There's no issue with the post", print_only=True)

        # try:
        #     comment_locator = self.ig.page.locator('svg[aria-label="Comment"]')
        #     like_locator = self.ig.page.locator('svg[aria-label="Like"]')
        #
        #     comment_visible = False
        #     like_visible = False
        #
        #     if comment_locator.count() > 0:
        #         comment_visible = comment_locator.first.is_visible(timeout=1000)
        #
        #     if like_locator.count() > 0:
        #         like_visible = like_locator.first.is_visible(timeout=1000)
        #
        #     if like_visible and not comment_visible:
        #         self.order.fail("Comment box is not visible")
        #         raise Exception("Comment box is not visible")
        #
        # except Exception as e:
        #     raise e

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
