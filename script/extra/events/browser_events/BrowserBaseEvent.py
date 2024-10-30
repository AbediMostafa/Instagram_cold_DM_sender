from time import sleep
import random


class BrowserBaseEvent:
    ig = None

    def __init__(self, ig):
        self.ig = ig

    def go_to_home(self):
        self.ig.account.add_cli('Going to home page ...')
        retries = 3
        for attempt in range(retries):
            try:
                try:
                    self.ig.page.get_by_role("link", name="Home Home").click(timeout=3000)
                except:
                    try:
                        self.ig.page.get_by_role("link", name="Home").click()
                    except:
                        self.ig.page.goto('https://www.instagram.com')

                break

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                sleep(2)
        self.ig.pause(4000, 6000)
        return self

    def go_to_profile_page(self):
        self.ig.account.add_cli('Going to Accounts profile page')
        self.ig.page.goto('https://www.instagram.com/accounts/edit/')
        self.ig.pause(4000, 5000)
        self.ig.page.goto("https://accountscenter.instagram.com/?entry_point=app_settings")
        self.ig.pause(3000, 4500)
        self.ig.account.add_cli('After profile load timeout')

    def go_to_threads(self):
        self.ig.account.add_cli('Going to threads page ...')
        try:
            self.ig.page.locator('a[aria-label*="Direct messaging"]').click(timeout=3000)

        except:
            try:
                self.ig.page.goto("https://www.instagram.com/direct/inbox/")
            except:
                try:
                    self.ig.page.locator('a[aria-label^="Direct messaging"]').first.click()
                except:
                    self.ig.page.locator('a[aria-label^="Direct messaging"]').last.click()

        self.ig.pause(4000, 6000)
        return self

    def get_thread_id(self):
        url = self.ig.page.url

        # Extract the thread_id from the URL
        return url.split('/')[-2]

    def scroll(self, times, min_length=300, max_length=1000):
        for __ in range(times):
            # Scroll down more often than up (e.g., 3-4 times down, 1 time up)
            down_scrolls = random.randint(2, 4)  # Random between 3 and 4

            # Perform the scroll down sequence
            for _ in range(down_scrolls):
                self.perform_smooth_scroll(scroll_direction=1, min_length=min_length, max_length=max_length)

            # Occasionally scroll up
            if random.random() < 0.45:  # 25% chance to scroll up
                self.perform_smooth_scroll(scroll_direction=-1, min_length=min_length, max_length=max_length)

            self.ig.pause(3000, 4500)

    def perform_smooth_scroll(self, scroll_direction, min_length=300, max_length=1000):
        # Randomly select a scroll length
        scroll_length = random.randint(min_length, max_length) * scroll_direction

        # Perform smooth scrolling using JavaScript
        self.ig.page.evaluate('''
                ({scrollLength}) => {
                    window.scrollBy({
                        top: scrollLength,
                        behavior: 'smooth'
                    });
                    return window.scrollY;  // Return the new scroll position of the page
                }
            ''', {'scrollLength': scroll_length})

        # Pause to simulate natural behavior
        self.ig.pause(1000, 2200)

    def go_and_click_on_lead_message(self, lead):
        try:
            self.go_to_lead_page_through_search(lead)
        except:
            self.go_to_lead_page_through_url(lead)

        self.ig.pause(5000, 5500)

        try:
            self.ig.page.get_by_role("button", name="Message").click()
        except:
            self.ig.page.locator('div:has-text("Message")').click()

    def go_to_lead_page_through_search(self, lead):
        try:
            search_button = self.ig.page.get_by_role("link", name="Search Search")
            search_button.wait_for()

            search_button.click()
        except:
            self.ig.page.get_by_role("link", name="Search").click()
        self.ig.pause(2000, 3000)

        try:
            self.ig.page.get_by_placeholder("Search").fill(lead.username)
        except:
            self.ig.page.locator("input[aria-label='Search input']").first.fill("lead.username")

        self.ig.pause(3000, 4500)
        self.ig.page.page.locator(f'a[href*="/{lead.username}/"]').first.click()

    def go_to_lead_page_through_url(self, lead):
        self.ig.page.goto(f'https://www.instagram.com/{lead.username}/')
