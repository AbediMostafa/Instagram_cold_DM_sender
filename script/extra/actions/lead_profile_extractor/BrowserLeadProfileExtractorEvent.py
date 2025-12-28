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

        user = json_response['data'].get('user')
        if not user:
            return

        # username must match current lead
        if user.get('username') != self.lead.username:
            return

        self.process_profile(user)

    def process_profile(self, user):
        username = user.get('username')
        full_name = user.get('full_name')
        bio = user.get('biography')
        profile_pic_url = user.get('profile_pic_url')
        id = user.get('id')

        self.ig.account.add_cli(f'Profile loaded: {username}, name:{full_name}')

        self.save_name_username(username, full_name)
        self.save_bio(bio)
        self.save_avatar(profile_pic_url)
        self.save_instagram_id(id)

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
        if not url:
            return

        now = datetime.now()
        month = now.month
        day = now.day

        relative_path = fr'uploads/avatar/{month}/{day}'
        storage_root = r'C:/Users/admin/Desktop/project/backend/storage/app/public'
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

    def init(self):
        self.ig.account.add_cli(f"Getting Leads profile ...")

        leads = Lead.select().where(Lead.instagram_id.is_null(True)).order_by(fn.Random()).limit(self.number_of_leads)

        for self.lead in leads:
            go_to_page(self.ig, f"https://www.instagram.com/{str(self.lead.username)}/", 'Lead')
            self.ig.pause(7000, 11000)
