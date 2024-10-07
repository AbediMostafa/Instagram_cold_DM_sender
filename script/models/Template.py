import datetime

from peewee import *
from .Base import BaseModel
from .Color import Color
from script.extra.helper import *
from .Category import Category


def delete(_type, text):
    return Template.delete().where(
        (Template.type == _type) & (Template.text == text)
    ).execute()


def get_a(_type, account=None):
    return Template.select().where(
        (Template.type == _type) & (Template.category == account.category)
    ).first()


class Template(BaseModel):
    text = CharField()
    caption = CharField()
    type = CharField()
    sub_type = CharField()
    carousel_id = CharField(null=True)
    uid = CharField(null=True)
    color = ForeignKeyField(Color, backref='templates', null=True)
    category = ForeignKeyField(Category, backref='templates', null=True)

    created_at = DateTimeField(null=True, default=datetime.datetime.now)

    def download_image(self, tmp=None):
        # If no tmp folder is provided, generate a random one
        if tmp is None:
            tmp = generate_random_folder()

        resource_url = get_post_url(self.text)

        # Extract the file extension from the URL (assuming URL ends with a valid extension)
        extension = os.path.splitext(resource_url)[1]  # Gets the extension, e.g., '.png' or '.jpg'

        resource_name = f'downloaded_image{extension}'
        image_path = os.path.join(tmp, resource_name)

        download_image(resource_url, image_path)

        return image_path

    class Meta:
        table_name = 'templates'
