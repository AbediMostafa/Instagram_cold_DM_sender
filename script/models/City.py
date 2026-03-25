from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
import random


class City(BaseWithTimeZoneModel):
    city_id = CharField()
    name = CharField()
    slug = CharField()
    is_used = SmallIntegerField(default=0)

    class Meta:
        table_name = 'cities'


def _try_claim_city():
    """
    Atomically claim one free city.
    """
    random_offset = random.randint(0, 5)

    candidates = list(
        City
        .select(City.id)
        .where(City.is_used == 0)
        .order_by(City.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            City
            .update(is_used=1)
            .where(
                (City.id == candidate.id) &
                (City.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return City.get_by_id(candidate.id)

    return None


def _try_reset_cities():
    """
    Reset cities with lock to prevent multiple threads from resetting.
    """
    from .Lock import Lock

    if not Lock.acquire('city_reset', duration_seconds=30):
        return False

    try:
        City.update(is_used=0).execute()
        return True

    finally:
        Lock.release('city_reset')


def get_next():
    """
    Select the next free city using atomic claiming.
    """
    print('Selecting city ...')

    for attempt in range(3):
        city = _try_claim_city()
        if city:
            print(f'Selected city : {city.name}')
            return city

    reset_done = _try_reset_cities()
    if reset_done:
        print('Cities reset completed')

    for attempt in range(3):
        city = _try_claim_city()
        if city:
            print(f'Selected city : {city.name}')
            return city

    print('No city available')
    return None
