from .Account import Account
from peewee import fn, JOIN


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
    Select the next free account, optionally filtered by tags.
    """
    print('Selecting account ...')

    query = free_account_query(tag_titles, specific_ids, service_id)

    # Refresh accounts if no free accounts exist
    if not query.exists():
        Account.update(is_used=False).execute()

    # Get the first non-used account with the specified tags
    next_account = (query
                    .order_by(Account.id)
                    .first())

    # Set the next account's is_used to True
    if next_account:
        next_account.is_used = True
        next_account.save()
        print(f'Selected account : {next_account.username}')

    return next_account


def get_next_account_for_api():
    query = Account.select().where(
        (Account.api_is_used == 0)
    )

    if not query.exists():
        Account.update(api_is_used=False).execute()

        # Get the first non-used account with the specified tags
    next_account = (query
                    .order_by(Account.id)
                    .first())

    # Set the next account's is_used to True
    if next_account:
        next_account.api_is_used = True
        next_account.save()
        print(f'Selected account : {next_account.id} -- {next_account.username}')

    return next_account


def get_next_profile():
    from .Profile import Profile

    query = Profile.select().where((Profile.is_used == 0))

    if not query.exists():
        Profile.update(is_used=False).execute()

    next_profile = (query
                    .order_by(Profile.id)
                    .first())

    # Set the next account's is_used to True
    if next_profile:
        next_profile.is_used = True
        next_profile.save()

    print(f'selected profile {next_profile.id}')

    return next_profile


def get_next_proxy(mobile_only=False):
    from .Proxy import Proxy

    query = Proxy.select().where((Proxy.is_used == 0))

    if mobile_only:
        query = query.where(Proxy.ip == 'x488.fxdx.in')

    if not query.exists():
        Proxy.update(is_used=False).execute()

    next_proxy = (query
                  .order_by(Proxy.id)
                  .first())

    # Set the next account's is_used to True
    if next_proxy:
        next_proxy.is_used = True
        next_proxy.save()

    print(f'selected Proxy {next_proxy.id}')

    return next_proxy


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
