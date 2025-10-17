import threading
import time
import requests

def crawl(link, delay=3):
    print(f"crawl started for {link}")
    res = requests.get(link)
    print(f"crawl result for {link} :")
    print(res.status_code)

links = [
    "https://python.org",
    "https://docs.python.org",
    "https://peps.python.org",
    "https://www.zoomit.ir",
    "https://docs.python.org/3/library/threading.html",
    "http://localhost:5173/dashboard",
]

# Start threads for each link
threads = []
for link in links:
    # Using `args` to pass positional arguments and `kwargs` for keyword arguments
    t = threading.Thread(target=crawl, args=(link,), kwargs={"delay": 2})
    threads.append(t)

# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()