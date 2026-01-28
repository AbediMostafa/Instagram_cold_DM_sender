from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.helper import *
import shutil
import random
from script.extra.helper import go_to_page
import urllib3
from script.models.Setting import Setting
from script.extra.playwright.base_actions.GetPostsAction import GetPostsAction
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.models.Url import Url

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

hashtags_list = [
    'instagram', 'instagood', 'explorepage', 'explore', 'viral', 'trending', 'reels',
    'reelsinstagram', 'reelsvideo', 'fyp', 'motivation', 'inspirational', 'quotes',
    'quoteoftheday', 'success', 'mindset', 'lifestyle', 'entrepreneur', 'business',
    'instadaily', 'instamood', 'follow', 'followme', 'like', 'likeforlikes', 'love',
    'photooftheday', 'instaquote', 'motivationdaily', 'fitnessmotivation', 'selfcare',
    'positivity', 'inspiration', 'goals', 'dreams', 'hardwork', 'nevergiveup',
    'successmindset', 'believe', 'entrepreneurmindset', 'viralreels', 'dailyquotes',
    'attitude', 'wisdom', 'mindsetmatters', 'growthmindset', 'focus', 'hustle',
    'ambition', 'dreambig', 'instareels', 'trendingnow', 'instafamous',
    'positivemindset', 'discipline', 'achiever', 'quote', 'motivationalquote',
    'deepquotes', 'happy', 'inspirationalquotes', 'mindsetcoach', 'selflove', 'vision',
    'lifegoals', 'keepgoing', 'dailyinspiration', 'justdoit', 'lifestyleblogger',
    'exploremore', 'successquotes', 'lifequotes', 'motivationoftheday', 'bestquotes',
    'instagramreels', 'model', 'artistic', 'creativelife', 'motivation101', 'bigdreams',
    'smartwork', 'quotesgram', 'inspirationdaily', 'instaphoto', 'influence',
    'instathoughts', 'epic', 'motivationalpost', 'powerfulquotes', 'entrepreneurlife',
    'businessowner', 'mindsetshift'
]

CAPTION_TEMPLATE = """
my manager tried to deport me, now this b*tch is getting payback 😠😠

after 3 yrs of busting my ass making fries, my manager LITERALLY called ice on me because i refused to cover a shift on my day off. she told them 'i didnt have papers' just to be petty (!!!)

luckily i got out of there before they showed up, but i'm not leaving quietly

here is the stuff corporate BEGS us to hide:

1. that "grilled" chicken is microwaved plastic. it comes in a bag and smells like wet dog before we heat it up. disgusting.

2. the ice machine? mega dirty. gross like a biohazard. i've seen brown sludge and beetles in there. if u get a drink, DO NOT get ice.

and the biggest secret they hide?

they have a monthly "Customer Satisfaction" budget that goes unused. they are legally required to give you a $100 store credit if you fill out the internal feedback form.

its only meant for employees, but screw 'em

{promo_url}

i also posted the direct link to claim it in the comments below 👇

use it before they patch the glitch. stick it to the man. ✊
"""

COMMENT_TEMPLATE = """
⚠️ UPDATE: They are trying to take this down bc non-employyes are not supposed to have it.

Type this link in your browser  to claim the $100 credit:

👉 {promo_url} 👈

 do it before they patch the glitch!!
"""


class BrowserPostFromFolderAndCommentEvent:
    base = None
    command = 0
    template = None
    image_path = 0
    caption = 0
    tmp = 0

    def __init__(self, ig):
        self.ig = ig
        self.posting_age = int(Setting.get_value("allowed_posting_age"))
        self.can_post = bool(int(Setting.get_value("can_send_post_from_folder")))

    def init(self):

        self.ig.account.add_cli(f"Allowed posting age : {self.posting_age}", print_only=True)
        self.ig.account.add_cli(f"Can post: {self.can_post}", print_only=True)

        if not self.can_post:
            return self.ig.account.add_cli(f"We're not allowed to post")

        if self.ig.account.get_passed_days_since_creation() < self.posting_age:
            return self.ig.account.add_cli(f"Account is not old enough to post image and comment")

        self.promo_url = Setting.get_next_promo_url()

        if not self.promo_url:
            return self.ig.account.add_cli(f"No promo URL available")

        self.ig.account.add_cli(f"Selected promo URL: {self.promo_url}")
        self.ig.account.add_cli(f"Posting an image from folder ...")

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
            # go_to_page(self.ig, "https://www.instagram.com/", "Home")
            self.ig.pause(3000, 4000)

    def generate_image(self):
        # "C:\Users\public\Desktop\project\script\posts\images"
        project_path = Setting.get_value('project_path')
        folder_path = fr"{project_path}\script\posts\images"
        files = os.listdir(folder_path)

        random_image = random.choice(files)

        self.ig.account.add_cli('Selected image:', random_image)

        self.image_path = os.path.join(folder_path, random_image)

    def generate_caption(self):
        selected = random.sample(hashtags_list, random.randint(8, 12))
        hashtags_text = ' '.join([f'#{h}' for h in selected])

        caption_text = CAPTION_TEMPLATE.format(promo_url=self.promo_url)
        self.caption = f"{caption_text}\n\n{hashtags_text}"

    def generate_comment(self):
        return COMMENT_TEMPLATE.format(promo_url=self.promo_url)

    def before_change_hook(self):
        self.command = self.ig.account.create_command('post image and comment', 'processing')

    def change_hook(self):
        try:
            self.ig.page.get_by_role("link", name="New post Create").click(timeout=3000)
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

        try:
            self.ig.page.locator(
                "input[accept='image/avif,image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(self.image_path)
        except:
            self.ig.page.locator(
                "input[accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(self.image_path)

        self.ig.pause(3000, 3500)
        try:
            self.ig.page.get_by_role("button", name="OK").click(timeout=3000)
        except:
            pass
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_label('Select crop').click()
        self.ig.pause(2000, 3500)

        try:
            self.ig.page.get_by_role('button', name='9:16').click(timeout=3000)

        except Exception as e:
            self.ig.account.add_cli(f"Couldn't find crop 9:16 trying second method {str(e)}")
            self.ig.page.get_by_role('button').filter(has_text='9:16').click()

        finally:
            self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").click()
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").click()
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_label("Write a caption...").fill(self.caption)
        self.ig.pause(3000, 4500)

        self.ig.page.get_by_role("button", name="Share").click()

        if self.wait_for_reel_shared():
            self.ig.account.add_cli("Reel shared confirmation received")
        else:
            self.ig.account.add_cli("Reel share confirmation NOT detected")

        DirectlyGoToAccountPageAction(self.ig).start(self.ig.account.username)

        self.ig.pause(3000, 4000)
        self.click_on_first_post()
        self.ig.pause(3000, 4000)

        self.save_post_url()

        self.add_comment()

    def wait_for_reel_shared(self, timeout_sec=70):
        import time

        start = time.time()

        while time.time() - start < timeout_sec:
            # Your post has been shared.
            try:
                if self.ig.is_visible_by_text('Your reel has been shared') or self.ig.is_visible_by_text('Your post has been shared'):
                    return True
            except TimeoutError:
                pass

            self.ig.account.add_cli("Post hasn't been posted yet ...")
            time.sleep(5)

        return False

    def click_on_first_post(self):
        self.ig.account.add_cli("Clicking on first post ...")
        posts = GetPostsAction(self.ig).start()
        post = posts.nth(0)
        post.locator('a').first.click(timeout=3000)

    def save_post_url(self):
        try:
            current_url = self.ig.page.url

            Url.create(
                command=self.command,
                url=current_url
            )

            self.ig.account.add_cli(f"Post URL saved: {current_url}")
        except Exception as e:
            import traceback
            self.ig.account.add_cli(f"Failed to save post URL: {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.add_cli("Image posted successfully")

    def add_comment(self):
        dynamic_comment = self.generate_comment()
        self.ig.page.get_by_placeholder("Add a comment…").fill(dynamic_comment, timeout=3000)
        self.ig.pause(1500, 2000)
        self.ig.page.get_by_role("button", name="Post", exact=True).click()
        self.ig.pause(1500, 2000)
