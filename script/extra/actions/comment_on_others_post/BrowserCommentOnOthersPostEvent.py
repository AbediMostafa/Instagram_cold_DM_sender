import random
import traceback

from script.models.Command import find_posts_to_comment
from script.models.Setting import Setting
from script.models.Url import Url


class BrowserCommentOnOthersPostEvent:
    command = None
    target_command = None
    target_url = None
    comment_posted = False

    def __init__(self, ig):
        self.ig = ig
        self.commenting_age = int(Setting.get_value("allowed_liking_and_commenting_age"))

    def init(self):
        if self.ig.account.get_passed_days_since_creation() < self.commenting_age:
            return self.ig.account.add_cli("Account is not old enough to engage")

        try:
            if not self.find_target_post():
                return

            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            self.handle_failure(e)

        finally:

            self.update_target_command_times()
            self.ig.pause(3000, 4000)

    def handle_failure(self, error):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.ig.account.add_cli(f"Engage failed: {str(error)}")
        self.ig.account.add_log(traceback.format_exc())

    def find_target_post(self):
        self.target_command = find_posts_to_comment(self.ig.account.id)

        if not self.target_command:
            self.ig.account.add_cli("No posts found to engage")
            return False

        self.target_url = self.target_command.get_url()

        if not self.target_url:
            self.ig.account.add_cli("Target post has no URL")
            return False

        self.ig.account.add_cli(f"Target: {self.target_url.url}")
        return True

    def before_change_hook(self):
        self.command = self.ig.account.create_command('post_engagement', 'processing')

    def change_hook(self):
        self.go_to_post()
        self.ig.pause(4000, 5000)

        self.check_fail_situations()
        self.dismiss_popup()

        comment_text = self.get_comment_text()
        self.ig.account.add_cli(f"Commenting: {comment_text[:30]}...")

        self.ig.page.get_by_placeholder("Add a comment…").fill(comment_text)
        self.ig.pause(4000, 5000)
        self.ig.page.get_by_role("button", name="Post", exact=True).click()
        self.ig.pause(4000, 5000)

        self.ig.account.add_cli("Comment posted")
        self.comment_posted = True

        self.save_post()
        self.maybe_like_post()
        self.maybe_repost()

    def update_target_command_times(self):
        if not self.target_command:
            return

        if self.comment_posted:
            self.target_command.times += 1
            if self.target_command.times == 1:
                self.target_command.commandable_id = self.ig.account.id
                self.target_command.commandable_type = 'App\\Models\\Account'
        else:
            # skip this post if failed
            self.target_command.times = 3

        self.target_command.save()

        status = "success" if self.comment_posted else "skipped"
        self.ig.account.add_cli(f"Target times updated: {self.target_command.times} ({status})")

    def maybe_repost(self):
        if random.randint(1, 10) <= 10:
            try:
                if self.try_repost():
                    self.ig.account.add_cli("Reposted")
            except Exception:
                pass

    def try_repost(self):
        selectors = [
            'svg[aria-label="Repost"]',
            'div[role="button"]:has(svg[aria-label="Repost"])',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    self.ig.pause(2000, 3000)

                    try:
                        self.ig.page.get_by_role("button", name="Repost").click(timeout=3000)
                        self.ig.pause(1500, 2500)
                        return True
                    except:
                        return True
            except:
                continue

        return False

    def maybe_like_post(self):
        if random.randint(1, 10) <= 7:
            try:
                if self.try_like():
                    self.ig.account.add_cli("Liked")
            except Exception:
                pass

    def try_like(self):
        if self.is_liked():
            return False

        selectors = [
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

    def go_to_post(self):
        self.ig.page.goto(self.target_url.url)

    def check_fail_situations(self):
        fail_messages = {
            'This account is private': 'Account is private',
            'Comments on this post have been limited': 'Comments limited',
            "Post isn't available": "Post unavailable",
            "The link may be broken": "Post unavailable",
            "the profile may have been removed": "Post unavailable",
            "There's an issue and the page could not be loaded": "Page load error",
        }

        for text, error in fail_messages.items():
            if self.ig.is_visible_by_text(text):
                raise Exception(error)

    def dismiss_popup(self):
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
            except:
                pass

        self.ig.pause(1000, 1200)

    def get_comment_text(self):
        comments = {
            0: "Wait I actually just got the code in my email?? I thought this was fake wtf",
            1: "For anyone asking, you have to type the link exactly how they wrote it. Worked for me.",
        }
        return comments.get(self.target_command.times, "Delete this lol before too many people see it and they patch it.")

    def save_post(self):
        try:
            if self.try_save():
                self.ig.account.add_cli("Saved")
        except Exception:
            pass

    def try_save(self):
        if self.is_saved():
            return False

        selectors = [
            'div[role="button"]:has(svg[aria-label="Save"])',
            'div.x14z9mp.xvc5jky div[role="button"]:has(svg[aria-label="Save"])',
            'section div[role="button"]:has(svg) >> nth=2',
            'div[data-visualcompletion="ignore-dynamic"] div[role="button"]:has(svg[aria-label="Save"])',
            'svg[aria-label="Save"]',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    self.ig.pause(1500, 2500)
                    if self.is_saved():
                        return True
            except:
                continue

        return False

    def is_saved(self):
        selectors = [
            'svg[aria-label="Remove"]',
            'svg[aria-label="Unsave"]',
            'div[role="button"]:has(svg[aria-label="Remove"])',
            'div[role="button"]:has(svg[aria-label="Unsave"])',
        ]

        for selector in selectors:
            try:
                if self.ig.page.locator(selector).first.count() > 0:
                    if self.ig.page.locator(selector).first.is_visible():
                        return True
            except:
                continue
        return False

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.save_comment_url()
        self.ig.account.add_cli("Engagement done")

    def save_comment_url(self):
        try:
            Url.create(
                command=self.command,
                url=self.target_url.url
            )
        except Exception:
            self.ig.account.add_log(traceback.format_exc())