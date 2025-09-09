import requests
import time

proxy = "http://mostafaaabedi-country-DE:EHRMBAG-FUVSHPY-STBMCL5-FVPSB1F-FZZ1GQG-40OBXSB-KDRAQ6S@private.residential.proxyrack.net:10000"  # change to your proxy
test_url = "https://httpbin.org/ip"  # test endpoint

proxies = {
    "http": proxy,
    "https": proxy
}

try:
    start = time.time()
    response = requests.get(test_url, proxies=proxies, timeout=10)
    latency = time.time() - start

    print("Status:", response.status_code)
    print("Proxy IP:", response.json())
    print("Latency: %.2f seconds" % latency)

except Exception as e:
    print("Proxy failed:", e)
