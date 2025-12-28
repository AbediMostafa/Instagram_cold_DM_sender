import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.extra.routes import check_processes

while True:
    print('Checking processes...')
    check_processes()
    time.sleep(60)
