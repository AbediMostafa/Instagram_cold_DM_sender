from .Account import Account
from .Color import Color
from peewee import fn, JOIN


def free_account_query(tag_titles=None):
    from .Tag import Tag
    from .Taggable import Taggable

    """
    Query to select accounts that are not used and are active.
    Optionally filter based on specific tags.
    """
    # Base query for free accounts
    query = Account.select().where(
        (Account.is_used == 0) &
        (Account.is_active == 1)
    )

    # If tag titles are provided, filter accounts based on tags
    if tag_titles:
        tags_to_include = Tag.select().where(Tag.title.in_(tag_titles))
        account_class = Taggable.get_taggable_class('Account')

        # Join with Taggable to filter accounts with specific tags
        query = (query
                 .join(Taggable, on=((Taggable.taggable_id == Account.id) &
                                     (Taggable.taggable_type == account_class)))
                 .where(Taggable.tag.in_(tags_to_include)))

    return query


def get_next_account(tag_titles=None):
    """
    Select the next free account, optionally filtered by tags.
    """
    print('Selecting account ...')

    query = free_account_query(tag_titles)

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


def get_first_proxy_with_less_accounts(exception_proxy_ids=None):
    from .Proxy import Proxy
    from script.extra.adapters.SettingAdapter import SettingAdapter

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
