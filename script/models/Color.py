import datetime
from peewee import *
from .Base import BaseModel


class Color(BaseModel):
    title = CharField()
    is_used = SmallIntegerField(default=0)

    class Meta:
        table_name = 'colors'


def get_a_free_color():
    return (Color
            .select()
            .where(Color.is_used == 0)
            .order_by(Color.id))


def get_next_color():
    free_color = get_a_free_color()

    if not free_color:
        Color.update(is_used=False).execute()
        free_color = get_a_free_color()

    free_color = free_color.first()

    if free_color:
        free_color.is_used = True
        free_color.save()

    return free_color
