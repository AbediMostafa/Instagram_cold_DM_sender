import requests
from uuid import uuid4

# url = 'https://thispersondoesnotexist.com/'
# headers = {'User-Agent': 'Mozilla/5.0'}
#
# resp = requests.get(url, headers=headers, timeout=10)
# resp.raise_for_status()
#
# filename = f'profile_pictures/image_{uuid4().hex}.jpg'
# with open(filename, 'wb') as f:
#     f.write(resp.content)
#
# print('saved:', filename)

proxies = {
    'http': 'http://02a17b0b64adbfb3524f:a885ff547a7d00e7@gw.dataimpulse.com:823',
    'https': 'http://02a17b0b64adbfb3524f:a885ff547a7d00e7@gw.dataimpulse.com:823'
}

r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=15)
print(r.text)
