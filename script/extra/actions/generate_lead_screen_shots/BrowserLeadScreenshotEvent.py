import os
import random
import traceback

from dotenv import load_dotenv
from script.extra.helper import go_to_page
from script.models.Lead import Lead

load_dotenv()


class BrowserLeadScreenshotEvent:
    ig = None

    # how many leads to process per execution
    lead_count = 10

    # read screenshot directory from .env so it works on both Windows and Linux
    # set LEAD_SCREENSHOT_DIR in your .env file, for example:
    # Windows: LEAD_SCREENSHOT_DIR=C:\Users\admin\Desktop\project\backend\storage\app\public\lead_screenshots
    # Linux:   LEAD_SCREENSHOT_DIR=/var/www/html/storage/app/public/lead_screenshots
    screenshot_dir = os.getenv('LEAD_SCREENSHOT_DIR', 'storage/app/public/lead_screenshots')

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        leads = Lead.get_leads_for_screenshot(self.lead_count)

        if not leads:
            self.ig.account.add_cli('No leads available for screenshot')
            return

        self.ig.account.add_cli(f'Found {len(leads)} leads to screenshot')

        # make sure the output directory exists
        os.makedirs(self.screenshot_dir, exist_ok=True)

        for lead in leads:
            try:
                self._take_screenshot(lead)
            except Exception as e:
                self.ig.account.add_cli(f'Failed to screenshot {lead.username}: {str(e)}')
                self.ig.account.add_log(f'Screenshot error for {lead.username}: {traceback.format_exc()}')

    def _take_screenshot(self, lead):
        url = f'https://www.instagram.com/{lead.username}/'
        self.ig.account.add_cli(f'Going to profile: {lead.username}')

        go_to_page(self.ig, url, 'Profile')

        # wait for the profile page to fully render
        self.ig.pause(5000, 7000)

        # check if the page actually loaded (not a 404 or error page)
        if self._is_page_not_found():
            self.ig.account.add_cli(f'Profile not found: {lead.username}, skipping')
            return

        # scroll down a bit so the first 3 rows of posts load into the DOM,
        # then scroll back up to capture everything from the top
        self.ig.page.mouse.wheel(0, random.randint(400, 600))
        self.ig.pause(2000, 3000)
        self.ig.page.mouse.wheel(0, -9999)
        self.ig.pause(1000, 1500)

        # take screenshot of the visible viewport area
        # this captures the profile header (avatar, bio, stats) plus first rows of posts
        file_name = f'{lead.id}.png'
        file_path = os.path.join(self.screenshot_dir, file_name)

        self.ig.page.screenshot(
            path=file_path,
            full_page=False,
            type='png'
        )

        # save relative path in DB (relative to public storage root)
        # the frontend builds the full URL using /storage/ prefix
        relative_path = f'lead_screenshots/{file_name}'
        lead.save_screenshot_path(relative_path)

        self.ig.account.add_cli(f'Screenshot saved for {lead.username}')

        # small pause between profiles to look more natural
        self.ig.pause(2000, 4000)

    def _is_page_not_found(self):
        """
        Check if Instagram shows a "page not found" message.
        This happens when the username doesn't exist or the account is deleted.
        """
        try:
            not_found = self.ig.page.locator('text="Sorry, this page isn\'t available."')
            return not_found.is_visible(timeout=2000)
        except Exception:
            return False