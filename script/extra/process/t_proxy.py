import requests

# Replace with your SOCKS5 proxy
PROXY = 'socks5://user-spszv0bfbq-country-us:7I9wxj6~vL1KijmxeE@isp.decodo.com:10001'

try:
    # Get real IP
    real_ip = requests.get(
        'https://api.ipify.org?format=json',
        timeout=15
    ).json()['ip']

    print(f'Real IP: {real_ip}')

    # Get IP through proxy
    proxy_ip = requests.get(
        'https://api.ipify.org?format=json',
        proxies={
            'http': PROXY,
            'https': PROXY,
        },
        timeout=15
    ).json()['ip']

    print(f'Proxy IP: {proxy_ip}')

    if proxy_ip != real_ip:
        print('✅ Proxy is working and IP changed.')
    else:
        print('❌ Proxy responded but IP did not change.')

except Exception as e:
    print(f'❌ Proxy failed: {e}')