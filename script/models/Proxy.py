from peewee import *
from .Base import BaseModel
import requests
import datetime
import pytz
import urllib.parse
import random
from script.extra.helper import tehran_now
from script.extra.exceptions import ProxyStuck


class Proxy(BaseModel):
    ip = CharField()  # proxy hostname (e.g., private.residential.proxyrack.net)
    port = IntegerField()
    username = CharField(null=True)
    password = CharField(null=True)
    state = CharField(null=True)
    type = CharField(null=True)
    is_used = SmallIntegerField(default=0)

    # new fields
    real_ip = CharField(null=True)
    real_ip_checked_at = DateTimeField(null=True)

    def deactivate(self):
        self.state = 'inactive'
        self.save()

    def set_is_used(self, is_used):
        self.is_used = is_used
        self.save()

    def set_real_ip(self, real_ip=None, real_ip_checked_at=None):

        if real_ip is not None:
            self.real_ip = real_ip

        if real_ip_checked_at is not None:
            self.real_ip_checked_at = real_ip_checked_at

        self.save()

    def to_requests_proxy(self):
        """
        Build proxy dict for requests library (SOCKS5).
        Returns format compatible with requests library proxies parameter.
        """
        if self.username and self.password:
            auth = f'{urllib.parse.quote(self.username)}:{urllib.parse.quote(self.password)}@'
        else:
            auth = ''

        proxy_url = f'socks5://{auth}{self.ip}:{self.port}'
        return {'http': proxy_url, 'https': proxy_url}

    def get_proxy_identifier(self):
        """
        Returns a string identifier for logging purposes.
        Shows host:port and real_ip if available.
        """
        identifier = f'{self.ip}:{self.port}'
        if self.real_ip:
            identifier += f' (real_ip: {self.real_ip})'
        return identifier

    class Meta:
        table_name = 'proxies'


def _build_requests_proxy(proxy: Proxy) -> dict:
    """Build a proxy dict for the requests library (supports SOCKS5)."""
    auth = f'{urllib.parse.quote(proxy.username)}:{urllib.parse.quote(proxy.password)}@'
    proxy_url = f'socks5://{auth}{proxy.ip}:{proxy.port}'
    return {'http': proxy_url, 'https': proxy_url}


def _fetch_external_ip_via_proxy(proxy: Proxy, timeout=10) -> str | None:
    try:
        timeout = int(timeout)
    except (TypeError, ValueError):
        timeout = 10
    proxies = _build_requests_proxy(proxy)
    endpoints = [
        'https://httpbin.org/ip',
        'https://ifconfig.co/ip',
        'https://api.ipify.org?format=json'
    ]
    headers = {'User-Agent': 'proxy-ip-checker/1.0'}
    for url in endpoints:
        try:
            r = requests.get(url, proxies=proxies, timeout=timeout, headers=headers)
            r.raise_for_status()
            text = r.text.strip()
            if 'json' in r.headers.get('Content-Type', ''):
                try:
                    j = r.json()
                    if isinstance(j, dict) and 'ip' in j:
                        return str(j['ip']).strip()
                except Exception:
                    pass
            import re
            m = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', text)
            if m:
                return m.group(1)
        except Exception as e:
            print(f"Proxy check failed for {url}: {type(e).__name__}: {e}")
            continue
    return None


def _try_claim_proxy(proxy_type):
    """
    Atomically claim one free proxy.
    """
    random_offset = random.randint(0, 10)

    if proxy_type == 'complex':
        proxy_types = ["global_datacenter", "datacenter"]
        query = (
            Proxy
            .select(Proxy.id)
            .where(
                (Proxy.is_used == 0) &
                (Proxy.type.in_(proxy_types))
            )
        )
    else:
        query = (
            Proxy
            .select(Proxy.id)
            .where(
                (Proxy.is_used == 0) &
                (Proxy.type == proxy_type)
            )
        )

    candidates = list(
        query
        .order_by(fn.Random())
        .offset(random_offset)
        .limit(5)
    )

    if not candidates:
        return None

    for candidate in candidates:
        updated = (
            Proxy
            .update(is_used=1)
            .where(
                (Proxy.id == candidate.id) &
                (Proxy.is_used == 0)
            )
            .execute()
        )

        if updated > 0:
            return Proxy.get_by_id(candidate.id)

    return None


def _try_reset_proxies(proxy_type):
    """
    Reset proxies with lock to prevent multiple threads from resetting.
    """
    from .Lock import Lock

    if not Lock.acquire('proxy_reset', duration_seconds=30):
        return False

    try:
        if proxy_type == 'complex':
            proxy_types = ["global_datacenter", "datacenter"]
            Proxy.update(is_used=0).where(Proxy.type.in_(proxy_types)).execute()
        else:
            Proxy.update(is_used=0).where(Proxy.type == proxy_type).execute()

        return True

    finally:
        Lock.release('proxy_reset')


def get_free_proxy(account=None, max_check_timeout=10, stuck_threshold_minutes=5, max_attempts=50):
    from .Setting import Setting

    proxy_type = Setting.get_value('proxy_type')
    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        next_proxy = _try_claim_proxy(proxy_type)

        if not next_proxy:
            reset_done = _try_reset_proxies(proxy_type)
            if reset_done:
                print('Proxies reset completed')
            continue

        print(f'Selected proxy : {next_proxy.ip}:{next_proxy.port}: {next_proxy.real_ip}')

        observed_ip = _fetch_external_ip_via_proxy(
            next_proxy,
            timeout=max_check_timeout
        )
        print(f'Observed IP : {observed_ip}')

        now = tehran_now()

        if not observed_ip:
            continue

        prev_ip = next_proxy.real_ip
        prev_checked = next_proxy.real_ip_checked_at

        if not prev_checked:
            next_proxy.set_real_ip(observed_ip, now)
            return next_proxy

        prev_checked = prev_checked.replace(tzinfo=None)

        if prev_ip == observed_ip:
            print(f'prev_ip : {prev_ip}, observed_ip : {observed_ip} are same')

            minutes = (now - prev_checked).total_seconds() / 60
            if minutes <= stuck_threshold_minutes:

                save_observed_ip(account, observed_ip, next_proxy)
                return next_proxy
            else:
                print(f'Proxy stuck for {minutes:.1f} min, trying next...')
                continue

        next_proxy.set_real_ip(observed_ip, now)
        save_observed_ip(account, observed_ip, next_proxy)

        return next_proxy

    raise RuntimeError('No valid rotating proxy found after max attempts')


def save_observed_ip(account, ip, proxy):
    from .Ip import Ip
    from .AccountIp import AccountIp

    ip_record, created = Ip.get_or_create(ip=ip, proxy=proxy, type=proxy.type)
    AccountIp.create(account=account, ip=ip_record)
