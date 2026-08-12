import subprocess
import time
import argparse
import os
import sys

# This file lives in project/script/, but `from script...` needs project/
# itself on the path — hence two dirnames, not one. (launcher.py gets away
# with one because it never imports from the package.)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Mobile analogue of launcher.py. On the web side the operator picks a window
# count; here the fleet size decides it — one worker process per active mobile,
# each pinned to its device with an explicit --mobile-id. As with the web
# side, these are independent OS processes (each its own memory, its own
# device, its own loop), so the only coordination channel is the database.

# Where the worker script lives (project/script), used as the default --path.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_mobile_ids():
    """
    Every device in the fleet gets a worker. What each one actually does is
    decided from the panel afterwards, on its row in the processes table: a
    worker with no workflow, or whose process status isn't 'running', simply
    parks itself and re-checks — the same remote on/off web workers have.
    """
    from script.models.Mobile import Mobile

    return [m.id for m in Mobile.select().order_by(Mobile.id)]


def main():
    parser = argparse.ArgumentParser(description='Launch one worker per mobile')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='delay between launches in seconds (default: 0.5)')
    parser.add_argument('--path', type=str, default=SCRIPT_DIR, help='script path')
    parser.add_argument('--script', type=str, default='mt.py',
                        help='per-worker entry script (default: mt.py)')
    parser.add_argument('--mobile-id', type=int, action='append', default=None,
                        help='explicit mobile id(s) to launch; repeatable. '
                             'Overrides auto-discovery.')
    args = parser.parse_args()

    mobile_ids = args.mobile_id if args.mobile_id else load_mobile_ids()

    if not mobile_ids:
        print('No mobiles in the database — run seed_mobiles.py first.')
        return

    print(f'Starting {len(mobile_ids)} mobile workers...')
    print(f'Path: {args.path}')
    print(f'Script: {args.script}')
    print('-' * 40)

    for i, mobile_id in enumerate(mobile_ids):
        subprocess.Popen(
            ['cmd', '/k',
             f'cd /d {args.path} && python {args.script} --mobile-id {mobile_id}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f'Started {i + 1}/{len(mobile_ids)} (mobile_id={mobile_id})')
        time.sleep(args.delay)

    print('-' * 40)
    print(f'Done! {len(mobile_ids)} workers opened.')
    print('Each registers itself in the processes table. Assign a workflow and '
          "set status to 'running' there to start them.")


if __name__ == '__main__':
    main()