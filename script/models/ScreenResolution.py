import datetime
from peewee import *
from .Base import BaseModel


class ScreenResolution(BaseModel):
    width = IntegerField()
    height = IntegerField()
    is_used = SmallIntegerField(default=0)

    class Meta:
        table_name = 'screen_resolutions'


def get_a_free_screen_resolution():
    return (ScreenResolution
            .select()
            .where(ScreenResolution.is_used == 0)
            .order_by(ScreenResolution.id))


def get_next_screen_resolution():
    free_screen_resolution = get_a_free_screen_resolution()

    if not free_screen_resolution:
        ScreenResolution.update(is_used=False).execute()
        free_screen_resolution = get_a_free_screen_resolution()

    free_screen_resolution = free_screen_resolution.first()

    if free_screen_resolution:
        free_screen_resolution.is_used = True
        free_screen_resolution.save()

    return free_screen_resolution
