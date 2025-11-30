import requests
import re
import json

url = 'https://www.charitynavigator.org/search?page=2&pageSize=10&_rsc=18cr4'

headers = {
    'accept': '*/*',
    'accept-language': 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22(root)%22%2C%7B%22children%22%3A%5B%22search%22%2C%7B%22children%22%3A%5B%22__PAGE__%3F%7B%5C%22page%5C%22%3A%5C%223%5C%22%2C%5C%22pageSize%5C%22%3A%5C%2210%5C%22%7D%22%2C%7B%7D%2C%22%2Fsearch%3Fpage%3D3%26pageSize%3D10%22%2C%22refresh%22%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%2Ctrue%5D%7D%2Cnull%2Cnull%5D',
    'next-url': '/search',
    'priority': 'u=1, i',
    'referer': 'https://www.charitynavigator.org/search?page=3&pageSize=10',
    'rsc': '1',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
}

cookies = {
    's_fid': '361AAD5A76350334-0D4D3A8BB18B5611',
    's_cc': 'true',
    'affinity': '"0e9759d8908dd13c"',
    'mbox': 'session#4b674529a9fe448d8d58c09ddd854f68#1761731253',
    's_sq': 'crtnavcharitynavigatorprod%3D%2526c.%2526a.%2526activitymap.%2526page%253DCharity%252520Navigator%2526link%253D2%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253DCharity%252520Navigator%2526pidt%253D1%2526oid%253DfunctionsK%252528%252529%25257B%25257D%2526oidt%253D2%2526ot%253DA'
}

response = requests.get(url, headers=headers, cookies=cookies)

# print(response.status_code)
# print(response.text)

match = re.search(r'"results":\s*(\[[\s\S]*?\])', response.text)
if match:
    json_part = match.group(1)
    print(json_part)
    charities = json.loads(json_part)
    print(charities)
    try:
        # 2️⃣ Parse it as JSON
        charities = json.loads(json_part)
        for c in charities:
            print(c['name'], '-', c['city'], c['state'], '-', c['rating'])
    except Exception as e:
        print('Parsing error:', e)
else:
    print('No results found.')
