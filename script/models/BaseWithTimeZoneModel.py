from peewee import *
from .Base import BaseModel
from script.extra.helper import tehran_now


class BaseWithTimeZoneModel(BaseModel):
    created_at = DateTimeField(null=True, default=tehran_now)
