from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
from .City import City
import random


class Location(BaseWithTimeZoneModel):
    location_id = CharField()
    name = CharField()
    slug = CharField()
    is_used = SmallIntegerField(default=0)
    city = ForeignKeyField(City, backref='locations', column_name='city_id')

    class Meta:
        table_name = 'locations'


def _try_claim_location():
    """
    Atomically claim one free city.
    """
    random_offset = random.randint(0, 5)

    candidates = list(
        Location
        .select(Location.id)
        .where(Location.is_used == 0)
        .order_by(Location.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Location
            .update(is_used=1)
            .where(
                (Location.id == candidate.id) &
                (Location.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Location.get_by_id(candidate.id)

    return None


def _try_reset_locations():
    """
    Reset cities with lock to prevent multiple threads from resetting.
    """
    from .Lock import Lock

    if not Lock.acquire('location_reset', duration_seconds=15):
        return False

    try:
        Location.update(is_used=0).execute()
        return True

    finally:
        Lock.release('location_reset')


def get_next():
    """
    Select the next free city using atomic claiming.
    """
    print('Selecting location ...')

    for attempt in range(3):
        location = _try_claim_location()
        if location:
            print(f'Selected location : {location.name}')
            return location

    reset_done = _try_reset_locations()
    if reset_done:
        print('Locations reset completed')

    for attempt in range(3):
        location = _try_claim_location()
        if location:
            print(f'Selected location : {location.name}')
            return location

    print('No location available')
    return None
