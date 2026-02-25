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


class BrowserLeadProfileExtractorEvent:
    command = None
    number_of_leads = None
    users = None
    lead = None

    def __init__(self, ig):
        self.ig = ig

        self.number_of_leads = random.randint(10, 15)
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

        self.ig.account.add_cli(f'Profile picture url : {profile_pic_url}')
        self.ig.account.add_cli(f'Profile loaded: {username}, name:{full_name}')

        if full_name:
            self.save_name_username(username, full_name)

        if bio:
            self.save_bio(bio)

        self.save_avatar(profile_pic_url)
        self.save_instagram_id(id)
        self.save_posts()

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

        def save(url, ext, type, relative_path, carousel_id=None, sub_type=None):

            project_path = Setting.get_value('project_path')
            storage_root = rf'{project_path}/backend/storage/app/public'

            full_dir = os.path.join(storage_root, relative_path)
            os.makedirs(full_dir, exist_ok=True)
            filename = f'{uuid.uuid4()}{ext}'
            full_path = os.path.join(full_dir, filename)
            text = os.path.join(relative_path, filename)

            try:
                r = requests.get(url, timeout=20)
                r.raise_for_status()
                with open(full_path, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                self.ig.account.add_cli(f"Media download failed: {e}")
                return

            Template.create(
                text=text,
                caption=caption,
                type=type,
                sub_type=sub_type,
                carousel_id=carousel_id,
            )

            self.ig.account.add_cli(
                f"Media saved: {shortcode} ({'video' if media_type == 2 else 'image'})"
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
            carousel_id = uuid.uuid4()
            relative_path = rf'video-post/{carousel_id}'

            videos = node.get('video_versions', [])
            thumbnails = node.get('image_versions2', [])
            if not videos:
                return

            video_url = videos[0]['url']
            video_ext = '.mp4'

            image_url = thumbnails.get('candidates')[0]['url']
            image_ext = '.mp4'

            save(video_url, video_ext, 'video-post', relative_path, carousel_id, 'video')
            save(image_url, image_ext, 'video-post', relative_path, carousel_id, 'image')


        else:
            return

    def save_name_username(self, username, full_name):
        Template.create(
            type='name-username',
            text=username,
            caption=full_name or ''
        )

        self.ig.account.add_cli(f"Lead name and username saved")

    def save_bio(self, bio):
        if not bio:
            return

        Template.create(
            type='bio',
            sub_type='text',
            text=bio,
            caption=''
        )

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

        Template.create(
            type='avatar',
            sub_type='image',
            text=f'{relative_path}/{filename}',
            caption=''
        )

        self.ig.account.add_cli(f"Lead avatar saved")

    def save_instagram_id(self, id):
        self.lead.instagram_id = id
        self.lead.save()
        self.ig.account.add_cli(f"Lead instagram id saved")

    def save_posts(self):
        pass

    def init(self):
        self.ig.account.add_cli(f"Getting Leads profile ...")

        leads = Lead.select().where(Lead.instagram_id.is_null(True)).order_by(fn.Random()).limit(self.number_of_leads)

        for self.lead in leads:
            go_to_page(self.ig, f"https://www.instagram.com/{str(self.lead.username)}/", 'Lead')
            self.ig.pause(7000, 11000)
