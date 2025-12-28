# proxies.py
from peewee import *
from .Base import BaseModel
import requests
import datetime
import pytz
import urllib.parse
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

    class Meta:
        table_name = 'proxies'


def _build_requests_proxy(proxy: Proxy) -> dict:
    """Build a proxy dict for the requests library (supports SOCKS5)."""
    auth = f'{urllib.parse.quote(proxy.username)}:{urllib.parse.quote(proxy.password)}@'
    proxy_url = f'socks5://{auth}{proxy.ip}:{proxy.port}'
    return {'http': proxy_url, 'https': proxy_url}


def _fetch_external_ip_via_proxy(proxy: Proxy, timeout=10) -> str | None:
    """Fetch the real external IP of a proxy."""
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
        except Exception:
            continue
    return None


def get_free_proxy(max_check_timeout=10, stuck_threshold_minutes=5, max_attempts=50):
    from .Setting import Setting

    proxy_type = Setting.get_value('proxy_type')
    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        query = Proxy.select().where(
            (Proxy.is_used == 0) & (Proxy.type == proxy_type)
        )

        if not query.exists():
            Proxy.update(is_used=0).execute()
            continue

        next_proxy = query.order_by(Proxy.id).first()
        if not next_proxy:
            continue

        next_proxy.set_is_used(1)
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
                return next_proxy
            else:
                print(f'Proxy stuck for {minutes:.1f} min, trying next...')
                continue

        next_proxy.set_real_ip(observed_ip, now)
        return next_proxy

    raise RuntimeError('No valid rotating proxy found after max attempts')
