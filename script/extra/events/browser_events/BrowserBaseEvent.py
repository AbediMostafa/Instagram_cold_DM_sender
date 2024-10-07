from time import sleep


class BrowserBaseEvent:
    ig = None

    def __init__(self, ig):
        self.ig = ig

    def go_to_profile_page(self):
        self.ig.account.add_cli('Going to Accounts profile page')
        self.ig.page.goto('https://www.instagram.com/accounts/edit/')
        self.ig.pause(4000, 5000)
        self.ig.page.goto("https://accountscenter.instagram.com/?entry_point=app_settings")
        self.ig.pause(3000, 4500)
        self.ig.account.add_cli('After profile load timeout')

    def go_to_threads(self):
        self.ig.account.add_cli('Going to threads page ...')
        retries = 3
        for attempt in range(retries):
            try:
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
                break
            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                sleep(2)
        self.ig.pause(4000, 6000)
        return self

    def get_thread_id(self):
        url = self.ig.page.url

        # Extract the thread_id from the URL
        return url.split('/')[-2]

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

    def scroll(self, times, length):

        for i in range(times):
            self.ig.account.add_cli(f'Scroll down for the {i} time ...')
            self.ig.page.mouse.wheel(0, length)
            # self.ig.page.mouse.wheel(0, 500)
            self.ig.pause(2000, 4000)
