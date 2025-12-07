import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Base import database

from script.models.CharityLead import CharityLead

import requests
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from peewee import *
from playhouse.postgres_ext import JSONField
from datetime import datetime

BASE_URL = 'https://www.charitynavigator.org'
CAUSE = 'Arts+and+culture'
STATES = 'AL'
PAGE_SIZE = 10
TOTAL_ITEMS = 39000
TOTAL_PAGES = TOTAL_ITEMS // PAGE_SIZE + 1

headers = {
    'accept': '*/*',
    'accept-language': 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'referer': 'https://www.charitynavigator.org/search',
    'rsc': '1',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
}

lock = Lock()


# =========================
# 🔍 Core scraping functions
# =========================
def extract_website(name, charity_url):
    """Fetch the charity page and extract its website URL."""

    try:
        req = requests.get(charity_url, headers=headers, timeout=15)
        html = req.text

        start = html.find('10:')
        if start == -1:
            return {'name': name, 'charity_page': charity_url, 'website': ''}

        open_brackets, end = 0, None
        for i, ch in enumerate(html[start:], start):
            if ch == '[':
                open_brackets += 1
            elif ch == ']':
                open_brackets -= 1
                if open_brackets == 0:
                    end = i + 1
                    break
        if not end:
            print('Not end')
            return {'name': name, 'charity_page': charity_url, 'website': ''}

        block = html[start + 2:end]
        match = re.search(r'"url":"(http[^"]+)"', block)
        website = match.group(1) if match else ''
        return {'name': name, 'charity_page': charity_url, 'website': website}

    except Exception as e:
        return {'name': name, 'charity_page': charity_url, 'website': f'ERROR: {e}'}


def save_charity_to_db(name, website, data):
    """Save each charity as a CharityLead record."""
    try:
        with lock:
            CharityLead.create(
                company_name=name,
                website=website,
                lead_type='charity_navigator',
                data=data,
            )
            print(f'💾 Saved to DB: {name} → {website}')
    except Exception as e:
        print(f'⚠️ DB insert failed for {name}: {e}')


def process_page(page):
    """Process one search page."""
    url = f'{BASE_URL}/search?page={page}&pageSize={PAGE_SIZE}&causes={CAUSE}&states={STATES}'
    print(f'\n🔹 Fetching page {page}/{TOTAL_PAGES}')
    try:
        response = requests.get(url, headers=headers, timeout=15)
        text = response.text

        print(text)
        return

        start = text.find('2:[')
        if start == -1:
            print('❌ No JSON start found.')
            return []

        open_brackets, end = 0, None
        for i, ch in enumerate(text[start:], start):
            if ch == '[':
                open_brackets += 1
            elif ch == ']':
                open_brackets -= 1
                if open_brackets == 0:
                    end = i + 1
                    break
        if not end:
            print('❌ Bracket parsing failed.')
            return []

        block = text[start + 2:end]
        data = json.loads(block)
        charities = data[3]['children'][1][3]['children'][3]['children'][3]['results']

        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = [
                executor.submit(extract_website, c['name'], f"{BASE_URL}{c['url']}")
                for c in charities
            ]
            for future in as_completed(futures):
                result = future.result()
                print(result)
                save_charity_to_db(result['name'], result['website'], result)

    except Exception as e:
        print(f'❌ Failed page {page}: {e}')


process_page(1)
# =========================
# 🚀 Main Execution
# =========================
# if __name__ == '__main__':
#     for page in range(1, TOTAL_PAGES + 1):
#         process_page(page)
#         time.sleep(1.5)
#
#     print('\n✅ Done! All charities saved in charity_leads table.')
