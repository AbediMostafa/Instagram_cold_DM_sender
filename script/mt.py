import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Per-worker entry point — the mobile mirror of t.py. Unlike a web worker,
# which claims whichever account it can from a shared pool, a mobile worker is
# pinned to exactly one device for its whole life, passed in with --mobile-id.
parser = argparse.ArgumentParser(description='Mobile worker for one DuoPlus device')
parser.add_argument('--mobile-id', type=int, default=None,
                    help='the mobiles.id this worker drives. Optional: without '
                         'it the worker uses the device assigned to its row in '
                         'the processes table.')
args = parser.parse_args()

print(f'PID: {os.getpid()}')
print(f'SERVER_IP from env: {os.getenv("SERVER_IP")}')
print(f'MOBILE_ID: {args.mobile_id}')

from script.extra.mobile.MobileProcessManager import MobileProcessManager

manager = MobileProcessManager(mobile_id=args.mobile_id)

while True:
    manager.run()