from .Account import Account
from .Color import Color
from peewee import fn, JOIN


def free_account_query():
    return Account.select().where(
        (Account.is_used == 0) &
        (Account.is_active == 1)
    )


def get_next_account():
    print('Selecting account ...')
    if not free_account_query().exists():
        Account.update(is_used=False).execute()

    # Get the first non-used account
    next_account = (free_account_query()
                    .order_by(Account.id)
                    .first())

    # Set the next account's is_current to True
    if next_account:
        next_account.is_used = True
        next_account.save()

    print(f'Selected account : {next_account.username} ')

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
