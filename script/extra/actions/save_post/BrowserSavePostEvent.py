from script.extra.helper import go_to_page
from script.models.OrderAction import get_next_action_for_account, mark_action_completed, release_stuck_actions, deduct_balance
from script.extra.exceptions import LinkIsNotCorrect
from script.extra.actions.BaseAction import BaseAction
from urllib.parse import urlparse


class BrowserSavePostEvent(BaseAction):
    command = None
    action = None
    order = None

    def init(self):
        self.pick_and_mark_action()
        self.ig.account.add_cli('Starting to save post ...')

        try:
            self.command = self.ig.account.create_command('save post', 'processing')
            self.post_url_validation()
            go_to_page(self.ig, self.order.target_link, 'Post Page')
            self.ig.pause(5000, 6000)
            self.dismiss_popup()
            self.ig.pause(1000, 1200)
            self.check_fail_situations()

            self.save_post()

            self.mark_action_sent()
            self.command.update_cmd('state', 'success')
            self.ig.pause(3500, 4500)

        except LinkIsNotCorrect as e:
            self.ig.account.add_cli(str(e), print_only=True)
            self.order.fail(str(e))

            if self.command:
                self.command.update_cmd('state', 'fail')

        except Exception as e:
            self.take_screenshot(command_id=self.order.id, fail_or_success='fail')
            self.ig.account.add_cli(str(e), print_only=True)

            self.action.reset_to_free()

            if self.command:
                self.command.update_cmd('state', 'fail')

    def pick_and_mark_action(self):
        self.action = get_next_action_for_account(self.ig.account, ['save_post'])

        if not self.action:
            raise Exception('There is no save_post order')

        self.order = self.action.order

        self.ig.account.add_cli(f'Selected order: {self.order.id}', print_only=True)
        self.ig.account.add_cli(f'Target link: {self.order.target_link}', print_only=True)

        if self.order.status == 'Pending':
            self.order.set_status_to('In progress')

    def post_url_validation(self):
        parsed = urlparse(self.order.target_link)

        self.ig.account.add_cli("Checking if is instagram page", print_only=True)

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            raise LinkIsNotCorrect("Invalid link, not an Instagram URL")

        path = parsed.path.strip('/').split('/')

        self.ig.account.add_cli("Checking if is a valid url", print_only=True)

        if len(path) == 1:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

        valid_first_segment = ["p", "reel", "tv"]

        self.ig.account.add_cli("Checking if is a valid post", print_only=True)

        if len(path) == 2 and path[0] in valid_first_segment:
            pass
        elif len(path) == 3 and path[1] in valid_first_segment:
            pass
        else:
            raise LinkIsNotCorrect("Not a valid Instagram post or reel")

    def dismiss_popup(self):
        if self.ig.is_visible_by_text("shared this with you") or \
           self.ig.is_visible_by_text("Stay up to date with"):
            try:
                self.ig.page.get_by_role("button", name="Not now").first.click(timeout=3000)
            except Exception as e:
                self.ig.account.add_cli(str(e))

    def check_fail_situations(self):
        self.ig.account.add_cli("Checking if account is private", print_only=True)
        if self.ig.is_visible_by_text('This account is private'):
            raise LinkIsNotCorrect('Account is private')

        if self.ig.is_visible_by_text("Post isn't available") or \
           self.ig.is_visible_by_text("The link may be broken") or \
           self.ig.is_visible_by_text("the profile may have been removed"):
            raise LinkIsNotCorrect("Post isn't available")

        self.ig.account.add_cli("Checking if There's an issue", print_only=True)
        if self.ig.is_visible_by_text("There's an issue and the page could not be loaded"):
            raise LinkIsNotCorrect("Something went wrong")

    def save_post(self):
        self.ig.account.add_cli("Attempting to save post...", print_only=True)

        if self.is_saved():
            self.ig.account.add_cli("Post is already saved", print_only=True)
            return True

        if self.try_save():
            self.ig.account.add_cli("Post saved successfully", print_only=True)
            return True

        raise Exception("Failed to save post")

    def try_save(self):
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

    def mark_action_sent(self):
        mark_action_completed(self.action)
        deduct_balance('save_post')
        release_stuck_actions()