from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.helper import *
import shutil
import random
import re
from script.extra.helper import go_to_page
import urllib3
from script.models.Setting import Setting
from script.extra.playwright.base_actions.GetPostsAction import GetPostsAction
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.models.Url import Url

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def spin(text):
    pattern = r'\{([^{}]+)\}'
    while re.search(pattern, text):
        text = re.sub(pattern, lambda m: random.choice(m.group(1).split('|')), text)
    return text


HASHTAGS_LIST = [
        "instagram",
        "instagood",
        "explorepage",
        "explore",
        "viral",
        "trending",
        "reels",
        "reelsinstagram",
        "reelsvideo",
        "fyp",
        "motivation",
        "inspirational",
        "quotes",
        "storytime",
        "exposed",
        "corporateexposed",
        "workplacestories",
        "toxicboss",
        "workplaceabuse",
        "whistleblower",
        "antiwork",
        "workersrights",
        "jobfromhell",
        "badboss",
        "toxicworkplace",
        "foryou",
        "reelsviral"
]

CAPTION_TEMPLATE = """
{my manager tried to deport me|my boss literally tried to get me deported|my manager went full psycho and tried to deport me}, now {this b*tch is getting payback|she's about to get what she deserves|it's payback time} 😠😠

{after 3 yrs|after 3 years|after years} of {busting my ass|breaking my back|grinding nonstop} making fries, my manager {LITERALLY|actually} {called ICE on me|reported me to ICE|tried to call immigration} because i {refused to cover a shift|wouldn't cover a shift} on my day off.
she {told them i didn't have papers|lied and said i was undocumented|claimed i had no papers} just to be {petty|spiteful|a bitch} (!!!)

{luckily|thank god} i {got out of there|left} before they showed up, but {i'm not leaving quietly|i'm not letting this slide|i'm not staying silent}

here is the stuff corporate {BEGS us to hide|doesn't want you to know|forces us to hide}:

1. that "{grilled|fresh grilled}" chicken is {microwaved|nuked} {plastic|in plastic}. it {comes in a bag|arrives in a bag} and {smells like wet dog|reeks} before we heat it up. {disgusting|nasty|vile}.

2. the ice machine? {mega dirty|filthy|absolutely disgusting}. {basically a biohazard|a straight biohazard}. i've seen {brown sludge|slime} and {beetles|bugs} in there. if u get a drink, {DO NOT get ice|skip the ice|never get ice}.

and the {biggest|worst} secret they hide?

they have a monthly "{Customer Satisfaction|Customer Feedback}" budget that goes {unused|unclaimed}. they are {legally required|required} to give you a {$100 store credit|$100 credit} if you fill out the {internal|official} feedback form.

it's {only meant for employees|supposed to be employee-only}, but {screw 'em|forget that|idc}

{promo_url}

{i also posted the direct link|the direct link is} in the comments below 👇

{use it before they patch the glitch|claim it before they fix it|get it before it's gone}. {stick it to the man|corporate can cry}. ✊
"""

COMMENT_TEMPLATE = """
⚠️ {UPDATE|UPDATE!!!}: {They are trying to take this down|They're deleting this|Corporate is panicking} bc {non-employees aren't supposed to have it|this isn't meant for customers}.

{Type this link in your browser|Go to this link manually} to claim the {$100 credit|$100 store credit}:

👉 {promo_url} 👈

{do it before they patch the glitch|use it before it's fixed|claim it ASAP}!!
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
        self.promo_url = None

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
            self.ig.pause(3000, 4000)

    def generate_image(self):
        project_path = Setting.get_value('project_path')
        folder_path = fr"{project_path}\script\posts\images"
        files = os.listdir(folder_path)

        random_image = random.choice(files)

        self.ig.account.add_cli(f"Random selected: {random_image}")

        self.image_path = os.path.join(folder_path, random_image)

    def generate_caption(self):
        selected = random.sample(HASHTAGS_LIST, random.randint(8, 12))
        hashtags_text = ' '.join([f'#{h}' for h in selected])

        temp_caption = CAPTION_TEMPLATE.replace('{promo_url}', '<<PROMO_URL>>')
        spun_caption = spin(temp_caption)
        caption_text = spun_caption.replace('<<PROMO_URL>>', self.promo_url)

        self.caption = f"{caption_text}\n\n{hashtags_text}"

    def generate_comment(self):
        temp_comment = COMMENT_TEMPLATE.replace('{promo_url}', '<<PROMO_URL>>')
        spun_comment = spin(temp_comment)
        return spun_comment.replace('<<PROMO_URL>>', self.promo_url)

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

        if not self.wait_for_reel_shared():
            self.ig.account.add_cli("Reel share confirmation NOT detected")
            self.command.update_cmd('state', 'fail')
            return False

        self.ig.account.add_cli("Reel shared confirmation received")

        DirectlyGoToAccountPageAction(self.ig).start(self.ig.account.username)

        self.ig.pause(3000, 4000)
        self.click_on_first_post()
        self.ig.pause(3000, 4000)

        self.save_post_url()
        self.add_comment()

        return True

    def wait_for_reel_shared(self, timeout_sec=140):
        import time

        start = time.time()

        while time.time() - start < timeout_sec:
            try:
                if self.ig.is_visible_by_text('Your reel has been shared') or self.ig.is_visible_by_text('Your post has been shared'):
                    return True
            except TimeoutError:
                pass

            self.ig.account.add_cli("Post hasn't been posted yet ...")
            time.sleep(7)

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