import requests
from requests.exceptions import RequestException, ProxyError, ConnectTimeout
import time

proxies_list = [
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10000",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10001",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10002",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10003",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10004",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10005",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10006",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10007",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10008",
    "239c1e03149f4688d9b7__cr.de:d4c552dfbab2110c@gw.dataimpulse.com:10009",
]

test_url = "https://httpbin.org/ip"

def test_proxy(proxy_str, index):
    try:
        user_pass, host_port = proxy_str.split("@")
        username, password = user_pass.split(":")
        host, port = host_port.split(":")

        proxy_url = f"socks5://{username}:{password}@{host}:{port}"

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        response = requests.get(test_url, proxies=proxies, timeout=10)

        try:
            ip = response.json().get("origin", "Unknown")
            print(f"[✓] #{index} Proxy {host}:{port} working. IP: {ip}")
        except ValueError:
            print(f"[✗] #{index} Proxy {host}:{port} returned non-JSON:\n{response.text[:200]}...")

    except (ProxyError, ConnectTimeout):
        print(f"[✗] #{index} Proxy {host}:{port} failed to connect (timeout or proxy error).")
    except Exception as e:
        print(f"[!] #{index} Unexpected error with proxy {proxy_str}: {e}")

if __name__ == "__main__":
    for idx, proxy in enumerate(proxies_list, 1):
        test_proxy(proxy, idx)
        time.sleep(0.5)  # Optional delay between tests