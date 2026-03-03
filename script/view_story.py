import urllib.parse
import urllib.request
import json

# The POST body as a clean Python dictionary
payload = {
    "av": "17841472313401641",
    "__d": "www",
    "__user": "0",
    "__a": "1",
    "__req": "y",
    "__hs": "20514.HYP%3Ainstagram_web_pkg.2.1...0",
    "dpr": "1",
    "__ccg": "UNKNOWN",
    "__rev": "1034299436",
    "__s": "i0xuty%3A6lhdr2%3A2pewkk",
    "__hsi": "7612604699503066917",
    "__dyn": (
        "7xeUjG1mxu1syUbFp41twpUnwgU7SbzEdF8aUco2qwJxS0DU2wx609vCwjE1EE2Cw8G11wBz81s8hwGxu786a3a1YwBgao6C0Mo2swlo8od8-U2zxe2GewGw9a361qwuEjUlwhEe87q0oa2-azqwt8d-2u2J0bS1LwTwKG1pg2fwxyo6O1FwlA3a3zhAq4rwIxeUnAwCAxW1oxe6U5q0EoKmUhw4rwXyEcE4y16wAwj8"
    ),
    "__csr": (
        "jNQeOMZ3I4T7NslOOhBh76RmZvRSBayAlfbGjICWykluyJ5BydelkVqQFVJ9aBUzCKALy-VaKEyqbVoiXSim9KeCHCy8VyqQQh3ryaJ92apAiAmnloWl2p8y9AhWjUgRhUpyRV8gGEDz4ELAzohh9Gxi9KAZ4gTlay6GUWuqiVFoLGcXDLzrx1qByuqmicim6Uhx648gyoR2K9xKcwDU88vw0rcU011VK7Hg9837Aw4Ha0lq34xoCah98980yS4o2_AAyU3bw5sg0FC04A60tMw0y6by9k4N0c8G1rD8t2Yg7EZ1e1wzogUaUb47E1Ok48f20tVi0XDwpUkg5K1LwfS1ohUB2VC1hwblU48wswn64z0AwkU1Mo0U22adx23W1y2Uwo07wE04ea01kmw1f62vw"
    ),
    "__hsdp": (
        "goA0BE4gah15Y6Hsy7h_yi89nEgRYPk4vJfVskaWq4xlwzyQiFx8rs5gO5XEw4pzrl1p3hweA4W8A8yUfUjgigyq3i6VS6SJaA9yUyp1LxK3e364FQ8e3S1wy9UK78ffxm5Q2a2u68fU9ayUy2qex96Cxa0ni3G9g1Z89E1Po0MGE1385Hw5vxW1Pg4S3u0Do3bU2Nwbm0MU0I60kl0qE6S7VC685S3-0CE3kg"
    ),
    "__hblp": (
        "1K0JoK2e3K7oDx5167kbxu1pxy3S58C1NCwgUqGmU8eE4S2222bUjAzUO4Q49EShaiVpU-7d7xa68lAwNxa2C4oSbG4obU-qi8KUKq5oqxKnV8Cq5Q2a2aUWazE8UOi7WKu8xCczEihFF8S0AU6i2y1iBwQykEK2-0hG0CE9E1JUlw4IwOwbhaagf8cU8U52E138nwZJoWq0kC7EG1Eg4qqu6olw9LBxm6o37zo7e0Jo33wiE1Ao3Axy483LwHgO3222ag6S7QlUhABwlUpwBwj8nwPU6a1Ng"
    ),
    "__sjsp": (
        "goA0BE4gah15Y6Hsysl4ju98wBux3nPdl11XA-m5ufwhQiEW6T1kcxuW816oSQEmgQo3F1N1i3-361vod8kDw"
    ),
    "__comet_req": "7",
    "fb_dtsg": "NAfsDgEzc08nfLjRYUB8mB3N-maW6mNiswB_Gx0DVx_TFBmyUq-WN0A:17865145036029998:1772255233",
    "jazoest": "26191",
    "lsd": "Pb-dDjosukmkLiR3-7tJln",
    "__spin_r": "1034299436",
    "__spin_b": "trunk",
    "__spin_t": "1772447652",
    "__crn": "comet.igweb.PolarisProfilePostsTabRoute",
    "fb_api_caller_class": "RelayModern",
    "fb_api_req_friendly_name": "PolarisStoriesV3ReelPageStandaloneQuery",
    "server_timestamps": "true",
    "variables": '{"reel_ids_arr":["71933425747"]}',
    "doc_id": "25761742843521329"
}

# Convert dictionary → URL-encoded bytes
data = urllib.parse.urlencode(payload).encode('utf-8')

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': (
        'dpr=1.25; ig_nrcb=1; ps_l=1; ps_n=1; datr=ZWufaFdNS2yrPxRlQuAWBo3N; '
        'ig_did=04AEB333-75FF-4C53-A772-1070F002C317; mid=aJ9rZQALAAE13gmYC2me3SvXICqF; '
        'csrftoken=smcCSynJFrDra0kp0NoKUvLs0SiOmOMA; ds_user_id=72413130446; '
        'sessionid=72413130446%3ALNk7IcNy4S8q3X%3A0%3AAYhGn0NMrZXQOyYLtFq6n1tPNrKyZoNO_EF96XXhBZE; '
        'rur="LDC\\,72413130446\\,1803983661:01fee1d5ddf2b91e94a2beac80df9ef83ca401eae3f4afba1255a3671d26c7136497ba8e"; '
        'wd=1536x290'
    ),
    'origin': 'https://www.instagram.com',
    'priority': 'u=1, i',
    'referer': 'https://www.instagram.com',
    'sec-ch-prefers-color-scheme': 'light',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="141.0.7390.107", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.107"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-asbd-id': '359341',
    'x-bloks-version-id': '29d0fd2d0bf67787771d758433b17814a729d9b4a57b07a39f1cc6507b480e39',
    'x-csrftoken': 'smcCSynJFrDra0kp0NoKUvLs0SiOmOMA',
    'x-fb-lsd': 'Pb-dDjosukmkLiR3-7tJln',
    'x-ig-app-id': '__cf_bm',
    'x-root-field-name': 'xdt_api__v1__feed__reels_media',
    'x-fb-friendly-name': 'PolarisStoriesV3ReelPageStandaloneQuery',

}
url = 'https://www.instagram.com/graphql/query'

req = urllib.request.Request(url, data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        print(result)
        # If you want to pretty-print the JSON response:
        # print(json.dumps(json.loads(result), indent=2))
except Exception as e:
    print("Request failed:", e)