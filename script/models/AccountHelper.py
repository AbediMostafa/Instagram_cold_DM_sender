from .Account import Account
from .Lock import Lock
from peewee import fn, JOIN
import random


def free_account_query(tag_titles=None, specific_ids=None, service_id=None):
    from .Tag import Tag
    from .Taggable import Taggable
    from script.models.Profile import Profile

    """
    Query to select accounts that are not used and are active.
    Optionally filter based on specific tags.
    """
    # Base query for free accounts
    query = Account.select().where(
        (Account.is_used == 0) &
        (Account.instagram_state == 'active')
    )

    # If specific IPs are provided, filter accounts based on IPs
    if specific_ids:
        query = query.where(Account.id.in_(specific_ids))

    # If tag titles are provided, filter accounts based on tags
    if tag_titles:
        tags_to_include = Tag.select().where(Tag.title.in_(tag_titles))
        account_class = Taggable.get_taggable_class('Account')

        # Join with Taggable to filter accounts with specific tags
        query = (query
                 .join(Taggable, on=((Taggable.taggable_id == Account.id) &
                                     (Taggable.taggable_type == account_class)))
                 .where(Taggable.tag.in_(tags_to_include)))

    if service_id:
        query = query.where(Account.service_id == service_id)

    return query


def get_next_account(tag_titles=None, specific_ids=None, service_id=None):
    """
    Select the next free account using atomic claiming.
    """
    print('Selecting account ...')

    for attempt in range(3):
        account = _try_claim_account(tag_titles, specific_ids, service_id)
        if account:
            print(f'Selected account : {account.username}')
            return account

    reset_done = _try_reset_accounts(service_id)
    if reset_done:
        print('Accounts reset completed')

    for attempt in range(3):
        account = _try_claim_account(tag_titles, specific_ids, service_id)
        if account:
            print(f'Selected account : {account.username}')
            return account

    print('No account available')
    return None


def _try_claim_account(tag_titles=None, specific_ids=None, service_id=None):
    """
    Atomically claim one free account.
    """
    from .Tag import Tag
    from .Taggable import Taggable

    random_offset = random.randint(0, 10)

    query = (
        Account
        .select(Account.id)
        .where(
            (Account.is_used == 0) &
            (Account.instagram_state == 'active')
        )
    )

    if specific_ids:
        query = query.where(Account.id.in_(specific_ids))

    if service_id:
        query = query.where(Account.service_id == service_id)

    if tag_titles:
        tags_to_include = Tag.select().where(Tag.title.in_(tag_titles))
        account_class = Taggable.get_taggable_class('Account')

        query = (
            query
            .join(Taggable, on=(
                (Taggable.taggable_id == Account.id) &
                (Taggable.taggable_type == account_class)
            ))
            .where(Taggable.tag.in_(tags_to_include))
        )

    candidates = list(
        query
        .order_by(Account.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Account
            .update(is_used=True)
            .where(
                (Account.id == candidate.id) &
                (Account.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Account.get_by_id(candidate.id)

    return None


def _try_reset_accounts(service_id=None):
    """
    Reset accounts with lock to prevent multiple threads from resetting.
    """
    if not Lock.acquire('account_reset', duration_seconds=30):
        return False

    try:
        query = Account.update(is_used=False).where(Account.instagram_state == 'active')

        if service_id:
            query = query.where(Account.service_id == service_id)

        query.execute()
        return True

    finally:
        Lock.release('account_reset')


def get_next_account_for_api():
    print('Selecting API account ...')

    for attempt in range(3):
        account = _try_claim_api_account()
        if account:
            print(f'Selected account : {account.id} -- {account.username}')
            return account

    reset_done = _try_reset_api_accounts()
    if reset_done:
        print('API accounts reset completed')

    for attempt in range(3):
        account = _try_claim_api_account()
        if account:
            print(f'Selected account : {account.id} -- {account.username}')
            return account

    print('No API account available')
    return None


def _try_claim_api_account():
    """
    Atomically claim one free API account.
    """
    random_offset = random.randint(0, 10)

    candidates = list(
        Account
        .select(Account.id)
        .where(Account.api_is_used == 0)
        .order_by(Account.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Account
            .update(api_is_used=True)
            .where(
                (Account.id == candidate.id) &
                (Account.api_is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Account.get_by_id(candidate.id)

    return None


def _try_reset_api_accounts():
    """
    Reset API accounts with lock.
    """
    if not Lock.acquire('api_account_reset', duration_seconds=30):
        return False

    try:
        Account.update(api_is_used=False).execute()
        return True
    finally:
        Lock.release('api_account_reset')


def get_next_profile():
    from .Profile import Profile

    print('Selecting profile ...')

    for attempt in range(3):
        profile = _try_claim_profile()
        if profile:
            print(f'selected profile {profile.id}')
            return profile

    reset_done = _try_reset_profiles()
    if reset_done:
        print('Profiles reset completed')

    for attempt in range(3):
        profile = _try_claim_profile()
        if profile:
            print(f'selected profile {profile.id}')
            return profile

    print('No profile available')
    return None


def _try_claim_profile():
    """
    Atomically claim one free profile.
    """
    from .Profile import Profile

    random_offset = random.randint(0, 10)

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
            .update(is_used=True)
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
    Reset profiles with lock.
    """
    from .Profile import Profile

    if not Lock.acquire('profile_reset', duration_seconds=30):
        return False

    try:
        Profile.update(is_used=False).execute()
        return True
    finally:
        Lock.release('profile_reset')


def get_next_proxy(mobile_only=False):
    from .Proxy import Proxy

    print('Selecting proxy ...')

    for attempt in range(3):
        proxy = _try_claim_proxy(mobile_only)
        if proxy:
            print(f'selected Proxy {proxy.id}')
            return proxy

    reset_done = _try_reset_proxies(mobile_only)
    if reset_done:
        print('Proxies reset completed')

    for attempt in range(3):
        proxy = _try_claim_proxy(mobile_only)
        if proxy:
            print(f'selected Proxy {proxy.id}')
            return proxy

    print('No proxy available')
    return None


def _try_claim_proxy(mobile_only=False):
    """
    Atomically claim one free proxy.
    """
    from .Proxy import Proxy

    random_offset = random.randint(0, 5)

    query = (
        Proxy
        .select(Proxy.id)
        .where(Proxy.is_used == 0)
    )

    if mobile_only:
        query = query.where(Proxy.ip == 'x488.fxdx.in')

    candidates = list(
        query
        .order_by(Proxy.id)
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Proxy
            .update(is_used=True)
            .where(
                (Proxy.id == candidate.id) &
                (Proxy.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Proxy.get_by_id(candidate.id)

    return None


def _try_reset_proxies(mobile_only=False):
    """
    Reset proxies with lock.
    """
    from .Proxy import Proxy

    lock_name = 'proxy_reset_mobile' if mobile_only else 'proxy_reset'

    if not Lock.acquire(lock_name, duration_seconds=30):
        return False

    try:
        query = Proxy.update(is_used=False)

        if mobile_only:
            query = query.where(Proxy.ip == 'x488.fxdx.in')

        query.execute()
        return True
    finally:
        Lock.release(lock_name)


def get_first_proxy_with_less_accounts(exception_proxy_ids=None):
    from .Proxy import Proxy
    from script.extra.adapters.SettingAdapter import SettingAdapter

    return Proxy.select().first()

    query = (Proxy
             .select(Proxy, Proxy.id, fn.COUNT(Account.id).alias('account_count'))
             .join(Account, JOIN.LEFT_OUTER)
             .where(Proxy.state == 'active'))

    if exception_proxy_ids:
        query = query.where(~Proxy.id.in_(exception_proxy_ids))

    return (query
            .group_by(Proxy.id)
            .having(fn.COUNT(Account.id) < SettingAdapter.max_account_for_one_proxy())
            .order_by(fn.COUNT(Account.id).desc())
            .first())


def update_accounts_proxy(proxy):
    next_proxy = get_first_proxy_with_less_accounts([proxy.id])
    query = Account.update(proxy=next_proxy).where(Account.proxy == proxy)
    query.execute()


def account_without_tags(tag_titles):
    from .Tag import Tag
    from .Taggable import Taggable

    tags_to_exclude = Tag.select().where(Tag.title.in_(tag_titles))
    account_class = Taggable.get_taggable_class('Account')

    excluded_accounts_subquery = (Taggable
    .select(Taggable.taggable_id)
    .where(
        (Taggable.taggable_type == account_class) &
        (Taggable.tag.in_(tags_to_exclude))
    ))

    query = (Account
             .select()
             .where(Account.id.not_in(excluded_accounts_subquery)))

    return list(query)


def get_storage_state(account):
    import json

    storage_state = account.web_session  # JSON string from DB

    try:
        storage_state = json.loads(storage_state)
        if isinstance(storage_state, str):  # Handle double encoding
            storage_state = json.loads(storage_state)
    except Exception as e:
        storage_state = {}

    return storage_state