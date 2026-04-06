from peewee import *
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
import random


class Country(BaseWithTimeZoneModel):
    country_code = CharField(unique=True)
    name = CharField()
    slug = CharField()
    is_used = SmallIntegerField(default=0)

    class Meta:
        table_name = 'countries'


def _try_claim_country():
    random_offset = random.randint(0, 5)

    candidates = list(
        Country
        .select(Country.id)
        .where(Country.is_used == 0)
        .order_by(Country.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Country
            .update(is_used=1)
            .where(
                (Country.id == candidate.id) &
                (Country.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Country.get_by_id(candidate.id)

    return None


def _try_reset_countries():
    from .Lock import Lock

    if not Lock.acquire('country_reset', duration_seconds=30):
        return False

    try:
        Country.update(is_used=0).execute()
        return True

    finally:
        Lock.release('country_reset')


def get_next():
    print('Selecting country ...')

    for attempt in range(3):
        country = _try_claim_country()
        if country:
            print(f'Selected country : {country.name}')
            return country

    reset_done = _try_reset_countries()
    if reset_done:
        print('Countries reset completed')

    for attempt in range(3):
        country = _try_claim_country()
        if country:
            print(f'Selected country : {country.name}')
            return country

    print('No country available')
    return None
