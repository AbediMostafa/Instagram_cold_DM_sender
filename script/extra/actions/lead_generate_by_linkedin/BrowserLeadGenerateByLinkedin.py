from script.extra.helper import go_to_page
from script.extra.playwright.base_actions.ScrollAction import ScrollAction
from script.models.EnrichedLead import EnrichedLead
from script.models.Lead import Lead
from script.models.Job import get_free_job
from bs4 import BeautifulSoup
import re
import requests
from urllib.parse import unquote
import urllib3

max_threads = 200
max_retries = 3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BrowserLeadGenerateByLinkedin:
    ig = None
    command = None
    job = None
    jobs = None
    company_data = {}
    jobs_url = 'https://www.linkedin.com/jobs/search?trk=guest_homepage-basic_guest_nav_menu_jobs'
    job_input = 'input#job-search-bar-keywords'
    location_input = 'input#job-search-bar-location'
    jobs_selector = 'ul.jobs-search__results-list li a.base-card__full-link '
    company_link = 'div.topcard__flavor-row span.topcard__flavor a.topcard__org-name-link'
    company_about_us_locator = 'p[data-test-id="about-us__description"]'
    company_name_locator = 'div.top-card-layout__entity-info  h1.top-card-layout__title'

    def __init__(self, ig):
        self.ig = ig
        job = get_free_job()
        self.scroll = ScrollAction(self.ig).start
        if job:
            self.job = job.title

    def init(self):

        try:
            self.command = self.ig.account.create_command('generate lead by linkedin', 'processing')
            self.generate_lead()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            self.ig.account.add_cli("Failed to generate lead by linkedin: " + str(e))

            if self.command:
                self.command.update_cmd('state', 'fail')

        finally:
            go_to_page(self.ig, "https://www.instagram.com/", "Instagram")

    def generate_lead(self):
        self.search_for_jobs()
        counter = 0

        for job in self.jobs:
            counter += 1
            new_tab = None

            try:
                job.click(timeout=5000)
                self.ig.pause(2000, 2500)  # give LinkedIn time to load job details

                with self.ig.context.expect_page() as new_page_info:
                    link = self.ig.page.locator(self.company_link).first
                    link.wait_for(state='visible', timeout=4000)
                    link.click(timeout=3000)

                self.ig.pause(2000, 3000)

                new_tab = new_page_info.value
                new_tab.wait_for_load_state('domcontentloaded')
                self.ig.pause(1000, 2000)
                self.dismiss(new_tab)
                self.scrape_company_data(new_tab)
                self.save_enriched_lead()

                new_tab.close()
                self.ig.pause(2000, 3000)

            except Exception as e:
                self.ig.account.add_cli(f'Problem processing job number {counter}: {str(e)}')
                self.dismiss(self.ig.page)

                if new_tab:
                    new_tab.close()

                self.ig.pause(1000, 2000)

    def search_for_jobs(self):
        go_to_page(self.ig, self.jobs_url, "Linkedin")
        self.ig.pause(3000, 4000)
        self.dismiss(self.ig.page)
        self.ig.pause(1000, 2000)
        self.ig.page.locator(self.job_input).fill(self.job)
        self.ig.pause(1000, 2000)
        self.ig.page.locator(self.location_input).fill('Worldwide')
        self.ig.pause(1000, 2000)
        self.ig.page.keyboard.press('Enter')
        self.ig.pause(3000, 5000)
        # self.ig.page.get_by_role("button", name="Any time").click(timeout=3000)
        # self.ig.pause(1000, 2000)
        # self.ig.page.get_by_label(re.compile(r'Past week', re.I)).check(timeout=3000)
        # self.ig.pause(2000, 3000)
        # self.ig.page.get_by_role("button", name="Done").click(timeout=3000)
        # self.ig.pause(3000, 5000)

        for _ in range(10):
            self.scroll(min_length=5000, max_length=6000, min_pause=1000, max_pause=3000)

            try:
                self.ig.page.get_by_role("button", name="See more jobs").click(timeout=3000)
                self.ig.pause(3000, 5000)
            except:
                pass

        self.jobs = self.ig.page.query_selector_all(self.jobs_selector)
        self.ig.account.add_cli(f'There are {len(self.jobs)} jobs available.')

    def scrape_company_data(self, page):

        # Select all the "div" sections under the <dl> (each one is a field)
        sections = page.query_selector_all('dl > div')

        for section in sections:
            label = section.query_selector('dt')
            value = section.query_selector('dd')

            if not label or not value:
                continue

            # Get text cleanly
            key = label.inner_text().strip().replace(':', '')
            val = value.inner_text().strip().replace('\n', ' ')

            # Normalize known keys (optional)
            key = key.lower().replace(' ', '_')
            self.company_data[key] = val

        self.company_data['about_us'] = page.locator(self.company_about_us_locator).first.text_content(timeout=3000)
        self.company_data['company_name'] = page.locator(self.company_name_locator).first.text_content(timeout=3000)

        if self.company_data['website']:
            self.company_data['instagram_username'] = self.extract_instagram_username(self.company_data['website'])

        return self.company_data

    def save_enriched_lead(self):
        """
        Save scraped company info into the EnrichedLead table.
        """
        # Normalize all keys to lowercase for consistency
        normalized = {k.lower(): v.strip() for k, v in self.company_data.items() if v and v.strip()}

        instagram_username = normalized.get('instagram_username')
        company_name = re.sub(r'\s+', ' ', normalized.get('company_name', '')).strip()

        try:
            Lead.get_or_create(username=instagram_username)
        except Exception as e:
            pass

        if instagram_username and self.lead_saved_before_in_database(instagram_username=instagram_username):
            self.ig.account.add_cli(f'Skipped saving {company_name or "Unknown"} (Instagram already exists)')
            return

        if not instagram_username and self.lead_saved_before_in_database(company_name=company_name):
            self.ig.account.add_cli(f'Skipped saving {company_name or "Unknown"} (Company already exists)')
            return

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

        self.ig.account.add_cli(f'Saved EnrichedLead record for {normalized.get('company_name') or "Unknown"}')

    def lead_saved_before_in_database(self, instagram_username=None, company_name=None):
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

    def extract_instagram_username(self, url):
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
                self.ig.pause(1000, 2000)

        return None

    def dismiss(self, page):
        try:
            page.get_by_role('button', name='Dismiss').click(timeout=3000)
        except:
            pass
