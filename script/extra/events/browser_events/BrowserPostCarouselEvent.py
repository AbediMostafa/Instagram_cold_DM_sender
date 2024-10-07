import random

from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import *
import random
import shutil


class BrowserPostCarouselEvent(InstagramMiddleware):
    base = None
    command = 0
    carousel_dict = None
    carousel_image = None
    image_path = 0
    caption = 0
    tmp = 0

    def execute(self):
        self.ig.account.add_cli(f"Posting an image ...")

        if self.ig.account.should_not_post('post carousel', random.randint(20, 24)):
            return self.ig.account.add_cli("Cant post an image today")

        self.carousel_dict = self.ig.account.get_a_carousel()

        if not self.carousel_dict:
            return self.ig.account.add_cli("We don't have any carousel")

        try:
            self.generate_images()
            self.generate_caption()
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem Posting Carousel : {str(e)}")
            # self.ig.pause(30000, 40000)
            self.ig.account.add_log(traceback.format_exc())

        finally:
            self.ig.page.goto("https://www.instagram.com/")
            self.ig.pause(3000, 4000)
            shutil.rmtree(self.tmp)

    def generate_images(self):

        self.tmp = generate_random_folder()

        for carousel_image in self.carousel_dict:
            image_path = carousel_image.download_image(self.tmp)

            # Here we use generate password to generate a unique word for image name
            carousel_image.image_path = process_image(image_path, self.tmp)

            self.ig.account.add_cli(f"Carousel image path : {carousel_image.image_path}")

    def generate_caption(self):
        first_carousel = self.carousel_dict[0]
        self.ig.account.add_cli('Generating caption...')

        prompt = f'rewrite this text without plagiarism please remove extra text and give me pure text:{first_carousel.caption}'
        self.caption = chat_ai(prompt)

    def before_change_hook(self):
        self.ig.account.set_state('post carousel', 'app_state')
        self.command = self.ig.account.create_command('post carousel', 'processing')

    def change_hook(self):
        try:
            self.ig.page.get_by_role("link", name="New post Create").click(timeout=3000)
        except:
            self.ig.page.get_by_role("link", name="New post").click(timeout=3000)

        self.ig.pause(2000, 3000)

        try:
            self.ig.page.locator('a[href="#"]:has(svg[aria-label="Post"])').click(timeout=3000)
        except Exception as e:
            try:
                self.ig.account.add_cli(f"Post button doesnt exists : {str(e)}")
                self.ig.page.locator('svg[aria-label="Post"]').click(timeout=3000)
            except Exception as e:
                pass

        self.ig.pause(3000, 3500)

        clicked_on_filter = False

        for carousel_image in self.carousel_dict:

            self.ig.page.locator(
                "input[accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(carousel_image.image_path)

            if not clicked_on_filter:
                self.ig.pause(2000, 2700)
                self.ig.page.locator("button").filter(has_text="Open media gallery").click()
                clicked_on_filter = True

            self.ig.pause(3000, 3500)

        # try:
        #     self.ig.page.get_by_role("button", name="Next").click()
        # except:
        self.ig.page.get_by_role("button", name="Next").nth(0).click()

        self.ig.pause(2000, 3500)

#         try:
#             self.ig.page.get_by_role("button", name="Next").click()
#         except:
        self.ig.page.get_by_role("button", name="Next").nth(0).click()

        self.ig.pause(2000, 3500)

        self.ig.page.get_by_label("Write a caption...").fill(self.caption)
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Share").click()
        self.ig.pause(14000, 16000)

        try:
            self.ig.page.get_by_role("button", name="Close").press("Escape")
        except:
            try:
                self.ig.page.get_by_role("button", name="Close").click()
            except:
                pass

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        for carousel_image in self.carousel_dict:
            self.ig.account.attach_template(carousel_image)

        self.ig.account.add_cli("Carousel posted successfully")
