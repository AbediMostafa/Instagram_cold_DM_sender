import requests
proxy_host = 'global.rotating.proxyrack.net'
proxy_port = '10227'
proxy_user = 'sajilepubugupa'
proxy_pass = 'WHVSVK9-F1THMWM-HDXU1WL-7WDLSBZ-KZFAMVN-SPXL653-MUCTOXX'
proxies = {
    'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
    'https': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
}

try:
    response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=15)
    print('Status Code:', response.status_code)
    print('Response:', response.text)
except Exception as e:
    print('Error:', str(e))