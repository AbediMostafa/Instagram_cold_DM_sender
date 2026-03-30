from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.helper import *
import shutil
import random
from script.extra.helper import go_to_page
import urllib3
from script.models.Setting import Setting
from script.models.Lead import Lead

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BrowserPostMediaEvent:
    base = None
    command = 0
    templates = None
    template_type = None
    image_path = None
    video_path = None
    lead = None
    caption = 0
    tmp = 0
    media_list_types = ['image-post', 'video-post', 'carousel']

    def __init__(self, ig):
        self.ig = ig
        self.posting_age = int(Setting.get_value("allowed_posting_age"))

    def init(self):
        if self.ig.account.get_passed_days_since_creation() < 3:
            raise Exception(f"Account is not old enough to Post Media")

        self.ig.account.add_cli(f"Allowed posting age : {self.posting_age}", print_only=True)

        if self.ig.account.get_passed_days_since_creation() < self.posting_age:
            return self.ig.account.add_cli(f"Account is not old enough to post image")

        self.ig.account.add_cli(f"Posting a media ...")

        try:
            self.generate_path()
            self.generate_caption()
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem Posting Image : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            if self.tmp:
                shutil.rmtree(self.tmp)
            go_to_page(self.ig, "https://www.instagram.com/", "Home")
            self.ig.pause(3000, 4000)

    def generate_path(self):
        self.tmp = generate_random_folder()
        self.templates, self.template_type, self.lead = Lead.get_a_media(self.ig.account, self.media_list_types)

        if not self.templates:
            raise Exception("We don't have any media for this account  ...")

        if self.template_type == 'video-post':

            for template in self.templates:
                template.path = template.download_image(self.tmp)

                if template.sub_type == 'video':
                    self.video_path = template.path
                    self.ig.account.add_cli(
                        f"video path : {template.path} Sub type: {template.sub_type} for {self.template_type}")

                elif template.sub_type == 'image':
                    self.image_path = process_image(template.path, self.tmp)
                    self.ig.account.add_cli(
                        f"image path : {template.path} Sub type: {template.sub_type} for {self.template_type}")

        else:

            for template in self.templates:
                template.path = template.download_image(self.tmp)
                template.path = process_image(template.path, self.tmp)

                self.ig.account.add_cli(f"image path : {template.path} for {self.template_type}")

    def generate_caption(self):
        self.ig.account.add_cli(f'Caption is {self.templates[0].caption}')
        self.caption = self.templates[0].caption

    def before_change_hook(self):
        self.ig.account.set_state('post image', 'app_state')
        self.command = self.ig.account.create_command('post media', 'processing')

    def change_hook(self):
        try:
            self.ig.page.get_by_role("link", name="New post Create").click(timeout=4000)
        except:
            self.ig.page.get_by_role("link", name="New post").click(timeout=4000)

        self.ig.pause(3000, 4000)

        try:
            self.ig.page.locator('svg[aria-label="Post"]').click(timeout=3000)
        except Exception as e:
            try:
                self.ig.account.add_cli(f"Post button doesnt exists : {str(e)}")
                self.ig.page.locator('a[href="#"]:has(svg[aria-label="Post"])').click(timeout=3000)
            except Exception as e:
                pass

        self.ig.pause(3000, 3500)

        if self.template_type == 'video-post':
            self.locate_media_path(self.video_path)

        else:

            clicked_on_filter = False

            for template in self.templates:
                self.locate_media_path(template.path)

                if self.template_type == 'carousel' and not clicked_on_filter:
                    self.ig.pause(2000, 2700)
                    self.ig.page.locator("button").filter(has_text="Open media gallery").click()
                    clicked_on_filter = True

                self.ig.pause(4000, 4500)

        self.ig.pause(3000, 3500)

        try:
            self.ig.page.get_by_role("button", name="OK").click(timeout=3000)
        except:
            pass
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").first.click()
        self.ig.pause(2000, 3500)

        if self.template_type == 'video-post' and self.image_path:
            self.ig.page.locator('div.html-div.xdj266r.x14z9mp>div>form input[accept="image/jpeg,image/png"]').nth(
                0).set_input_files(self.image_path)
            self.ig.page.locator('input[accept="image/jpeg,image/png"]').nth(0).set_input_files(self.image_path)
            self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").first.click()
        self.ig.pause(2000, 3500)

        if self.caption:
            self.ig.page.get_by_label("Write a caption...").fill(self.caption)
            self.ig.pause(3000, 4500)

        self.ig.page.get_by_role("button", name="Share").click()

        if self.wait_for_reel_shared():
            self.ig.account.add_cli("Reel shared confirmation received")
        else:
            self.ig.account.add_cli("Reel share confirmation NOT detected")

    def locate_media_path(self, path):
        try:
            self.ig.page.locator(
                "input[accept='image/avif,image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(path)
        except:
            self.ig.page.locator(
                "input[accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(path)

    def wait_for_reel_shared(self, timeout_sec=70):
        import time

        start = time.time()

        while time.time() - start < timeout_sec:
            try:
                if self.ig.is_visible_by_text('Your reel has been shared') or self.ig.is_visible_by_text(
                        'Your post has been shared'):
                    return True
            except TimeoutError:
                pass

            self.ig.account.add_cli("Post hasn't been posted yet ...")
            time.sleep(5)

        return False

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.add_cli("Media posted successfully")

        if self.lead.account is None:
            self.lead.set_account(self.ig.account)

        for template in self.templates:
            self.ig.account.attach_template(template)
