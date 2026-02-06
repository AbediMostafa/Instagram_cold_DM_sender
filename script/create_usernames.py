import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
from collections import Counter
from script.models.AutomationQueue import AutomationQueue

THREADS = 400
results = []
lock = threading.Lock()


def worker(tid):
    job = AutomationQueue.pop_first()
    results.append(job.id)


threads = []

start = time.time()

for i in range(THREADS):
    t = threading.Thread(target=worker, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

end = time.time()

print('Time:', end - start)
print('Total picked:', results)
print('Total picked:', len(results))
print('Unique picked:', len(set(results)))

dupes = [k for k, v in Counter(results).items() if v > 1]
print('Duplicates:', dupes)
