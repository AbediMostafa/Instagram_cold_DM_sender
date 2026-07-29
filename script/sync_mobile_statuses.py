import sys
import os
import time
import argparse
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from script.models.Mobile import Mobile
from script.extra.mobile.base.BaseDuoPlus import BaseDuoPlus
from script.extra.helper import tehran_now

# The status endpoint is batch (up to 100 phones per call), so one sync pass
# over the whole fleet costs ceil(N/100) API calls instead of N. Workers still
# poll their own phone directly during boot; this sync just keeps the panel
# fresh and gives a cheap fleet-wide view.
BATCH_LIMIT = 100
DEFAULT_INTERVAL = 60


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def sync_once():
    mobiles = list(Mobile.select())
    if not mobiles:
        print('[sync] no mobiles in DB')
        return

    by_duo_id = {m.duo_id: m for m in mobiles}

    for chunk in chunked(list(by_duo_id.keys()), BATCH_LIMIT):
        statuses = BaseDuoPlus.batch_status(chunk)

        for duo_id, code in statuses.items():
            mobile = by_duo_id.get(duo_id)
            if mobile is None:
                continue

            # Plain field writes on purpose: this must NOT touch updated_at,
            # which is the worker heartbeat used by the stuck-reset.
            Mobile.update(status=code).where(Mobile.id == mobile.id).execute()
            print(f'[sync] {mobile.name} ({duo_id}) -> status={code}')

        # Report phones the API said nothing about — usually a wrong duo_id.
        missing = set(chunk) - set(statuses.keys())
        for duo_id in missing:
            print(f'[sync] WARNING: no status returned for {duo_id}')


def main():
    parser = argparse.ArgumentParser(description='Central DuoPlus status sync')
    parser.add_argument('--once', action='store_true', help='run one pass and exit')
    parser.add_argument('--interval', type=int, default=DEFAULT_INTERVAL,
                        help=f'seconds between passes (default {DEFAULT_INTERVAL})')
    args = parser.parse_args()

    while True:
        try:
            sync_once()
        except Exception as e:
            # The sync is best-effort infrastructure: log and keep looping,
            # same self-healing philosophy as the workers.
            print(f'[sync] pass failed: {e}')
            traceback.print_exc()

        if args.once:
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()
