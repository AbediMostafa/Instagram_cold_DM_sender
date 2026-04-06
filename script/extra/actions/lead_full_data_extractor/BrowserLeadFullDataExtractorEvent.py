from random import random
import os
from script.models.Lead import Lead
from script.models.Template import Template
from peewee import *
import random
from script.extra.helper import go_to_page
from datetime import datetime
import requests
import uuid
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
from script.extra.exceptions import NotAReachableAccount


class BrowserLeadFullDataExtractorEvent:
    command = None
    number_of_leads = None
    users = None
    lead = None

    def __init__(self, ig):
        self.ig = ig
        self.post_count = 0
        self.scroll = ScrollAction(self.ig).start

        # self.number_of_leads = random.randint(1, 3)
        self.number_of_leads = 1
        self.ig.page.on("response", lambda response: self.handle_response(response))

    def handle_response(self, response):
        if 'graphql/query' not in response.url:
            return

        try:
            json_response = response.json()
        except:
            return

            # must contain user.profile info
        if not json_response.get('data'):
            return

        data = json_response['data']
        user = data.get('user')

        if user and user.get('username') == self.lead.username:
            self.process_profile(user)

        timeline = data.get('xdt_api__v1__feed__user_timeline_graphql_connection')

        if timeline:
            self.process_timeline(timeline)

    def process_profile(self, user):
        username = user.get('username')
        full_name = user.get('full_name')
        bio = user.get('biography')
        profile_pic_url = user.get('hd_profile_pic_url_info').get('url')
        id = user.get('id')

        self.ig.account.add_cli(f'Profile loaded: {username}, name:{full_name}')

        if full_name:
            self.save_name_username(username, full_name)

        if bio:
            self.save_bio(bio)

        self.save_avatar(profile_pic_url)
        self.save_instagram_id(id)

    def process_timeline(self, timeline):
        edges = timeline.get('edges', [])
        if not edges:
            return

        for edge in edges:
            node = edge.get('node')
            if not node:
                continue

            self.save_media(node)

    def save_media(self, node):
        from script.models.Setting import Setting

        media_type = node.get('media_type')  # 1=image, 2=video, 8=carousel
        shortcode = node.get('code')
        caption = node.get('caption')

        if caption:
            caption = caption.get('text')

        now = datetime.now()
        month = now.month
        day = now.day

        def save(url, ext, type, relative_path, carousel_id=None, sub_type=None, uid=None):

            project_path = Setting.get_value('project_path')
            storage_root = rf'{project_path}/backend/storage/app/public'

            full_dir = os.path.join(storage_root, relative_path)
            os.makedirs(full_dir, exist_ok=True)
            filename = f'{uuid.uuid4()}{ext}'
            full_path = os.path.join(full_dir, filename)
            text = f"{relative_path}/{filename}"

            try:
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                with open(full_path, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                self.ig.account.add_cli(f"Media download failed: {e}")
                return

            template = Template.create(
                text=text,
                caption=caption,
                type=type,
                sub_type=sub_type,
                carousel_id=carousel_id,
                uid=uid,
            )

            self.save_lead_template(template)

            self.ig.account.add_cli(
                f"Media saved: {shortcode} ({media_type})"
            )
            pass

        # IMAGE
        if media_type == 1:
            relative_path = rf'uploads/image-post/{month}/{day}'
            candidates = node.get('image_versions2', {}).get('candidates', [])
            if not candidates:
                return

            url = candidates[0]['url']
            ext = '.jpg'

            save(url, ext, 'image-post', relative_path)

        # VIDEO
        elif media_type == 2:
            # http://207.189.164.112/storage/uploads/video-post/a7cd5688-8b7b-464a-822b-c47fc8d3b184\95a16b07-0a98-4140-841e-cadf097bc029.mp4
            carousel_id = uuid.uuid4()
            relative_path = rf'uploads/video-post/{carousel_id}'

            videos = node.get('video_versions', [])
            thumbnails = node.get('image_versions2', [])
            if not videos:
                return

            video_url = videos[0]['url']
            video_ext = '.mp4'

            image_url = thumbnails.get('candidates')[0]['url']
            image_ext = '.jpg'

            save(video_url, video_ext, 'video-post', relative_path, carousel_id, 'video')
            save(image_url, image_ext, 'video-post', relative_path, carousel_id, 'image')


        elif media_type == 8:
            medias = node.get('carousel_media')
            carousel_id = uuid.uuid4()

            for uid, media in enumerate(medias, start=1):
                relative_path = rf'uploads/carousel/{carousel_id}'
                candidates = media.get('image_versions2', {}).get('candidates', [])

                url = candidates[0]['url']
                ext = '.jpg'

                save(url, ext, 'carousel', relative_path, carousel_id, 'image', uid)





        else:
            return

    def save_name_username(self, username, full_name):

        template = Template.create(
            type='name-username',
            text=username,
            caption=full_name or ''
        )

        self.save_lead_template(template)
        self.ig.account.add_cli(f"Lead name and username saved")

    def save_bio(self, bio):

        if not bio:
            return

        template = Template.create(
            type='bio',
            text=bio,
            caption=''
        )

        self.save_lead_template(template)
        self.ig.account.add_cli(f"Lead bio saved")

    def save_avatar(self, url):
        from script.models.Setting import Setting

        if not url:
            return

        now = datetime.now()
        month = now.month
        day = now.day

        relative_path = fr'uploads/avatar/{month}/{day}'
        project_path = Setting.get_value('project_path')
        storage_root = rf'{project_path}/backend/storage/app/public'
        full_dir = os.path.join(storage_root, relative_path)

        os.makedirs(full_dir, exist_ok=True)

        ext = '.jpg'
        filename = f'{uuid.uuid4()}{ext}'
        full_path = os.path.join(full_dir, filename)

        r = requests.get(url, timeout=15)
        r.raise_for_status()

        with open(full_path, 'wb') as f:
            f.write(r.content)

        template = Template.create(
            type='avatar',
            sub_type='image',
            text=f'{relative_path}/{filename}',
            caption=''
        )

        self.save_lead_template(template)
        self.ig.account.add_cli(f"Lead avatar saved")

    def save_instagram_id(self, id):
        self.lead.instagram_id = id
        self.lead.save()
        self.ig.account.add_cli(f"Lead instagram id saved")

    def init(self):
        self.ig.account.add_cli(f"Getting Leads profile ...")

        for _ in range (self.number_of_leads):

            self.lead = Lead.select().where(Lead.instagram_id.is_null(True)).order_by(fn.Random()).first()
            go_to_page(self.ig, f"https://www.instagram.com/{str(self.lead.username)}/", 'Lead')
            self.ig.pause(7000, 11000)

            try:
                self.handle_page_breaks()
            except NotAReachableAccount as e:
                self.ig.account.add_cli(str(e))
                continue

            self.extract_post_count()
            self.ig.pause(6000, 8000)
            number_of_scrolls = int(self.post_count / 10)
            number_of_scrolls = min(number_of_scrolls, 10)
            print(f'Number Of Scrolls : {number_of_scrolls}')

            for i in range(number_of_scrolls):
                self.scroll(min_length=7000, max_length=8000, min_pause=4000, max_pause=6000)

    def save_lead_template(self, template):
        from script.models.LeadTemplate import LeadTemplate

        LeadTemplate.create(lead=self.lead, template=template)

    def extract_post_count(self):
        try:
            post_element = self.ig.page.locator('span:has-text("posts")').first

            text = post_element.inner_text()
            post_count = text.split()[0]

            if 'K' in post_count:
                self.post_count = int(float(post_count.replace('K', '').replace(',', '')) * 1000)
            else:
                self.post_count = int(post_count.replace(',', ''))
        except Exception as e:
            self.ig.account.add_cli(f'Problem extracting post counts : {str(e)}')
            self.post_count = 200

        print(f'Post Count : {self.post_count}')  # 554

    def handle_page_breaks(self):
        error_texts = [
            "This profile is private",
            "This account is private",
            "Sorry, this page isn't available",
            "Page is not available",
            "This page isn't available",
            "the page may have been removed",
            "The link you followed may be broken",
        ]

        for text in error_texts:
            if self.ig.is_visible_by_text(text):
                raise NotAReachableAccount(text)
