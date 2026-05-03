from peewee import *
from .Proxy import Proxy
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel
import random


class Profile(BaseWithTimeZoneModel):
    title = CharField()
    profile_id = CharField()
    profile_number = CharField()
    folder = CharField()
    is_used = SmallIntegerField(default=0)
    proxy = ForeignKeyField(Proxy, backref='profiles', null=True)

    class Meta:
        table_name = 'profiles'


def _try_claim_profile():
    """
    Atomically claim one free profile.
    """
    random_offset = random.randint(0, 5)

    candidates = list(
        Profile
        .select(Profile.id)
        .where(Profile.is_used == 0)
        .order_by(Profile.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Profile
            .update(is_used=1)
            .where(
                (Profile.id == candidate.id) &
                (Profile.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Profile.get_by_id(candidate.id)

    return None


def _try_reset_profiles():
    """
    Reset profiles with lock to prevent multiple threads from resetting.
    """
    from .Lock import Lock

    if not Lock.acquire('profile_reset', duration_seconds=30):
        return False

    try:
        Profile.update(is_used=0).execute()
        return True

    finally:
        Lock.release('profile_reset')


def get_next():
    """
    Select the next free profile using atomic claiming.
    """
    print('Selecting profile ...')

    for attempt in range(3):
        profile = _try_claim_profile()
        if profile:

            print(f'Selected profile : {profile.profile_id}')
            return profile

    reset_done = _try_reset_profiles()
    if reset_done:
        print('Profiles reset completed')

    for attempt in range(3):
        profile = _try_claim_profile()
        if profile:
            print(f'Selected profile : {profile.profile_id}')
            return profile

    print('No profile available')
    return None