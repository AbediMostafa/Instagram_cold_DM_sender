import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Base import database
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
import re
import json
import urllib3
from urllib.parse import unquote, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor

from script.models.CharityLead import CharityLead, get_free_charity_lead

max_threads = 150
max_retries = 2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_social_links(url, max_retries=3):
    """
    Fetch a page and extract Instagram username and LinkedIn URL.
    Returns dict: {'instagram': 'username' or None, 'linkedin': 'https://...'/None}
    Returns None if neither found.
    """

    def clean_url(u):
        if not u:
            return None
        u = unquote(u).strip()
        u = re.sub(r'\s+', '', u)  # remove whitespace/newlines
        u = re.split(r'Externallinkfor', u, flags=re.I)[0]  # remove garbage after domain
        if not u.startswith(('http://', 'https://')):
            u = 'https://' + u
        return u

    def extract_real_url(possible_redirect):
        """
        Handle google.com/url?q=... style redirects and similar wrappers.
        If no redirect structure is detected returns original string.
        """
        try:
            parsed = urlparse(possible_redirect)
            net = (parsed.netloc or '').lower()
            # handle google redirect pattern
            if 'google.com' in net and parsed.path.startswith('/url'):
                query = parse_qs(parsed.query)
                if 'q' in query:
                    return unquote(query['q'][0])
            # common redirect param examples: ?u= or ?url= or ?q=
            qs = parse_qs(parsed.query)
            for key in ('q', 'url', 'u'):
                if key in qs:
                    return unquote(qs[key][0])
        except Exception:
            pass
        return possible_redirect

    url = clean_url(url)
    if not url:
        return None

    social_links = {'instagram': None, 'linkedin': None}

    # full headers + cookies you provided
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }

    cookies = {
        "__stripe_mid": "435279df-eaf4-41e2-af2c-d685aaa9ce104abba1",
        "__stripe_sid": "0af97e4c-7baf-4f27-8dff-0685e7b8f8e6a3bd43",
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, cookies=cookies, timeout=12, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # --- Instagram detection: scan every <a href=...>
            for link in soup.find_all('a', href=True):
                href = link['href']
                href = extract_real_url(href)
                href = unquote(href)
                if re.search(r'(instagram\.com/)', href, re.I):
                    # remove trailing params/fragments and path parts
                    username = re.sub(r'(https?://)?(www\.)?instagram\.com/', '', href, flags=re.I).split('/')[0]
                    username = username.split('?')[0].strip()
                    if username:
                        social_links['instagram'] = username
                        break

            # --- LinkedIn detection: scan every <a href=...>
            for link in soup.find_all('a', href=True):
                href = link['href']
                href = extract_real_url(href)
                href = unquote(href)
                if re.search(r'(linkedin\.com/)', href, re.I):
                    href = re.sub(r'[\?#].*$', '', href)  # drop query/fragment
                    if not href.startswith(('http://', 'https://')):
                        href = 'https://' + href
                    social_links['linkedin'] = href
                    break

            # --- Optional Instagram fallback: data-options etc.
            if not social_links['instagram']:
                instagram_data = soup.find(attrs={'data-options': True})
                if instagram_data:
                    match = re.search(r'"avatars":\{.*?"([^"]+)"', str(instagram_data))
                    if match:
                        fallback_href = match.group(1)
                        username = re.sub(r'(https?://)?(www\.)?instagram\.com/', '', fallback_href).split('/')[0]
                        social_links['instagram'] = username.split('?')[0]

            if not social_links['instagram'] and not social_links['linkedin']:
                return None

            return social_links

        except requests.RequestException as e:
            # network/HTTP specific errors
            print(f"Request error for {url} (Attempt {attempt + 1}): {e}")
            time.sleep(1)
        except Exception as e:
            # any other parsing/safety errors
            print(f"Error processing {url} (Attempt {attempt + 1}): {e}")
            time.sleep(1)

    return None


def lead_saved_before_in_database(instagram=None, company_name=None):
    """
    Check if a lead already exists in the database.
    Builds a base query and applies filters dynamically.
    """
    query = CharityLead.select()

    if instagram:
        query = query.where(CharityLead.instagram == instagram)

    return query.exists()


def process_lead():
    lead = get_free_charity_lead()

    while lead:
        website = lead.website

        if not website:
            print(f"Lead {lead.id}: No Website found")
            lead = get_free_charity_lead()
            continue

        print(f"Lead {lead.id}: Extracted website {website}...")

        socials = extract_social_links(website)

        if not socials:
            print(f"Lead {lead.id}: No Social founds")
            lead = get_free_charity_lead()
            continue

        instagram = socials['instagram']
        linkedin = socials['linkedin']

        if instagram:

            if lead.record_exists(instagram=instagram):
                lead.set_is_duplicated(1)
                print(f"Lead {lead.id}: Duplicated instagram username {instagram}")

            else:
                print(f"Lead {lead.id}: Found Instagram {instagram}, saving...")
                lead.save_socials(instagram=instagram)

        else:
            print(f"Lead {lead.id}: No Instagram username found")

        if linkedin:
            if lead.record_exists(linkedin=linkedin):
                lead.set_is_duplicated(1)
                print(f"Lead {lead.id}: Duplicated linkedin username {linkedin}")

            else:
                print(f"Lead {lead.id}: Found Linkedin {linkedin}, saving...")
                lead.save_socials(linkedin=linkedin)

        else:
            print(f"Lead {lead.id}: No Linkedin username found")

        lead = get_free_charity_lead()


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit 20 threads to start processing leads concurrently
        futures = [executor.submit(process_lead) for i in range(max_threads)]

        # Wait for all threads to finish
        for f in futures:
            f.result()
