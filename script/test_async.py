import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script.models.Base import database
from script.models.Proxy import get_free_proxy, _build_requests_proxy
from script.models.Job import Job, get_free_job

import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
import re

import urllib3

from script.models.EnrichedLead import EnrichedLead
from script.models.Lead import Lead

max_threads = 200
max_retries = 3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_instagram_username(url):
    def clean_url(u):
        if not u:
            return None
        u = unquote(u).strip()
        u = re.sub(r'\s+', '', u)  # remove whitespace/newlines
        # remove garbage after domain like "Externallinkfor..."
        u = re.split(r'Externallinkfor', u, flags=re.I)[0]
        if not u.startswith(('http://', 'https://')):
            u = 'https://' + u
        return u

    url = clean_url(url)
    if not url:
        return None

    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            }

            response = requests.get(url, headers=headers, timeout=20, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try finding Instagram links
            for link in soup.find_all("a", href=re.compile(r"(https?://)?(www\.)?instagram\.com/")):
                href = link.get('href')
                if href:
                    username = re.sub(r"(https?://)?(www\.)?instagram\.com/", "", href).split('/')[0]
                    return username.split('?')[0]

            # Fallback: check for data-options JSON
            instagram_data = soup.find(attrs={'data-options': True})
            if instagram_data:
                match = re.search(r'"avatars":{.*?"([^"]+)"', str(instagram_data))
                if match:
                    href = match.group(1)
                    username = re.sub(r"(https?://)?(www\.)?instagram\.com/", "", href).split('/')[0]
                    return username.split('?')[0]

            return None

        except Exception as e:
            print(f"Error processing {url} (Attempt {attempt + 1}): {e}")
            time.sleep(1)

    return None


def save_enriched_lead(company_data):
    """
    Save scraped company info into the EnrichedLead table.
    """
    # Normalize all keys to lowercase for consistency

    # Convert Tag objects to strings
    for key in ['company_name', 'about_us', 'industry', 'company_size', 'headquarters', 'type', 'founded',
                'specialties']:
        if company_data.get(key) and hasattr(company_data[key], 'get_text'):
            company_data[key] = company_data[key].get_text(strip=True)

    # Normalize strings
    normalized = {k.lower(): v.strip() for k, v in company_data.items() if isinstance(v, str) and v.strip()}

    instagram_username = normalized.get('instagram_username')
    company_name = re.sub(r'\s+', ' ', normalized.get('company_name', '')).strip()

    if instagram_username and lead_saved_before_in_database(instagram_username=instagram_username):
        print(f'Skipped saving {company_name or "Unknown"} (Instagram already exists)')
        return

    if not instagram_username and lead_saved_before_in_database(company_name=company_name):
        print(f'Skipped saving {company_name or "Unknown"} (Company already exists)')
        return

    if instagram_username:
        try:
            Lead.get_or_create(username=instagram_username)
        except Exception as e:
            pass

    lead = EnrichedLead()
    lead.fill(
        company_name=company_name,
        about_us=re.sub(r'\s+', ' ', normalized.get('about_us', '')).strip(),
        website=normalized.get('website'),
        industry=normalized.get('industry'),
        company_size=normalized.get('company_size'),
        headquarters=normalized.get('headquarters'),
        type=normalized.get('type'),
        founded=normalized.get('founded'),
        specialties=normalized.get('specialties'),
        instagram_username=instagram_username
    )

    print(f'Saved EnrichedLead record for {normalized.get('company_name') or "Unknown"}')


def lead_saved_before_in_database(instagram_username=None, company_name=None):
    """
    Check if a lead already exists in the database.
    Builds a base query and applies filters dynamically.
    """
    query = EnrichedLead.select()

    if instagram_username:
        query = query.where(EnrichedLead.instagram_username == instagram_username)

    if company_name:
        query = query.where(EnrichedLead.company_name == company_name)

    return query.exists()


def scrape_linkedin_companies(job_keyword, proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    keyword_encoded = quote(job_keyword)
    proxies = _build_requests_proxy(proxy)
    base_url = f'https://www.linkedin.com/jobs/search?keywords={keyword_encoded}&location=Worldwide&trk=public_jobs_jobs-search-bar_search-submit'

    print(f"Searching LinkedIn jobs for '{job_keyword}'...")

    company_links = set()

    # Step 1: Request main jobs page
    try:
        response = requests.get(base_url, headers=headers, proxies=proxies, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.select('a[href*="/company/"]'):
                link = a_tag.get('href').split('?')[0]
                company_links.add(link)

            print(f"Found {len(company_links)} company URLs from first page")
        else:
            print(f"Failed to fetch main jobs page ({response.status_code})")
    except Exception as e:
        print(f"Error fetching first page: {e}")

    # Step 2: Fetch 'see more' pages (increment start by 25 up to 300)
    for start in range(25, 301, 25):
        api_url = (
            f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?'
            f'keywords={keyword_encoded}&location=Worldwide&trk=public_jobs_jobs-search-bar_search-submit&start={start}'
        )

        print(f"Fetching extra jobs from start={start}")
        try:
            r = requests.get(api_url, headers=headers, proxies=proxies, timeout=15)
            if r.status_code != 200:
                print(f"Skipped {api_url} (Status: {r.status_code})")
                continue

            api_soup = BeautifulSoup(r.text, 'html.parser')
            before = len(company_links)
            for a_tag in api_soup.select('a[href*="/company/"]'):
                link = a_tag.get('href').split('?')[0]
                company_links.add(link)
            added = len(company_links) - before
            print(f"Added {added} new companies (total {len(company_links)})")

        except Exception as e:
            print(f"Error fetching {api_url}: {e}")

        time.sleep(1)

    print(f"Total {len(company_links)} unique company URLs for '{job_keyword}'")

    # Step 3: Scrape each company page
    for company_url in company_links:
        try:
            r_company = requests.get(company_url, headers=headers, proxies=proxies, timeout=15)
            company_soup = BeautifulSoup(r_company.text, 'html.parser')

            company_data = {
                'linkedin_url': company_url,
                'company_name': company_soup.select_one('h1.top-card-layout__title'),
                'about_us': company_soup.select_one('p[data-test-id="about-us__description"]'),
                'industry': company_soup.select_one('div[data-test-id="about-us__industry"] dd'),
                'company_size': company_soup.select_one('div[data-test-id="about-us__size"] dd'),
                'headquarters': company_soup.select_one('div[data-test-id="about-us__headquarters"] dd'),
                'type': company_soup.select_one('div[data-test-id="about-us__organizationType"] dd'),
                'founded': company_soup.select_one('div[data-test-id="about-us__foundedOn"] dd'),
                'specialties': company_soup.select_one('div[data-test-id="about-us__specialties"] dd'),
            }

            website_dd = company_soup.select_one('div[data-test-id="about-us__website"] dd a')
            company_data['website'] = website_dd.get_text(strip=True) if website_dd else None
            company_data['instagram_username'] = extract_instagram_username(company_data['website'])

            save_enriched_lead(company_data)

        except Exception as e:
            print(f"Failed to process {company_url}: {e}")

        time.sleep(1)


def worker_thread():
    """Worker that picks one job and one proxy and runs the scraper."""
    job = get_free_job()
    if not job:
        print('No jobs available.')
        return

    proxy = get_free_proxy(type='datacenter')

    if not proxy:
        print('No proxies available.')
        return

    scrape_linkedin_companies(job.title, proxy)
    print(f'[{job.title}] Done.')


def main():
    import threading

    total_jobs = Job.select().count()
    print(f'Total jobs in database: {total_jobs}')

    threads = []
    for _ in range(total_jobs):
        t = threading.Thread(target=worker_thread)
        threads.append(t)
        t.start()
        time.sleep(1)  # short delay to avoid proxy conflicts

    for t in threads:
        t.join()

    print('✅ All jobs completed.')


if __name__ == '__main__':

    main()
