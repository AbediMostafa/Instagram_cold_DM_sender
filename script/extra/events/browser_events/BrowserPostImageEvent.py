from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import *
import shutil
import random


class BrowserPostImageEvent(InstagramMiddleware):
    base = None
    command = 0
    template = None
    image_path = 0
    caption = 0
    tmp = 0

    def execute(self):
        self.ig.account.add_cli(f"Posting an image ...")

        if self.ig.account.should_not_post('post image', random.randint(20, 24)):
            return self.ig.account.add_cli("Cant post an image today")

        self.template = self.ig.account.get_a_free_template('image-post')

        if not self.template:
            return self.ig.account.add_cli(f"We don't have a post image for this account")

        try:
            self.generate_image()
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
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)

    def generate_image(self):
        self.tmp = generate_random_folder()
        image_path = self.template.download_image(self.tmp)

        self.image_path = process_image(image_path, self.tmp)

    def generate_caption(self):
        prompt = f'rewrite this text without plagiarism please remove extra text and give me pure text:{self.template.caption}'
        self.caption = chat_ai(prompt)

    def before_change_hook(self):
        self.ig.account.set_state('post image', 'app_state')
        self.command = self.ig.account.create_command('post image', 'processing')

    def change_hook(self):
        try:
            self.ig.page.get_by_role("link", name="New post Create").click()
        except:
            self.ig.page.get_by_role("link", name="New post").click()

        self.ig.pause(3000, 4000)

        try:
            self.ig.page.locator('a[href="#"]:has(svg[aria-label="Post"])').click(timeout=3000)
        except Exception as e:
            try:
                self.ig.account.add_cli(f"Post button doesnt exists : {str(e)}")
                self.ig.page.locator('svg[aria-label="Post"]').click(timeout=3000)
            except Exception as e:
                pass

        self.ig.pause(3000, 3500)
        self.ig.page.locator(
            "input[accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
            0).set_input_files(self.image_path)
        self.ig.pause(3000, 3500)

        self.ig.page.get_by_role("button", name="Next").click()
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").click()
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_label("Write a caption...").fill(self.caption)
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Share").click()
        self.ig.pause(15000, 17000)

        try:
            self.ig.page.get_by_role("button", name="Close").press("Escape")
        except:
            try:
                self.ig.page.get_by_role("button", name="Close").click()
            except:
                pass

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.attach_template(self.template)
        self.ig.account.add_cli("Image posted successfully")
