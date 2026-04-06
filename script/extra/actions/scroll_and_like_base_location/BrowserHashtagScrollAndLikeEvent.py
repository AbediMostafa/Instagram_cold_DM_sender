from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
from script.models.City import City
import random
import re


class BrowserHashtagScrollAndLikeEvent(InstagramMiddleware):
    """
    Warm-up event that searches for a hashtag via the Instagram UI and likes random posts.

    Simulates real user behavior by opening search through the sidebar, typing a hashtag,
    picking a random result from the suggestions, then scrolling and liking posts.

    The sidebar always has a Search icon. If Explore is also in the sidebar, clicking
    Search opens a side panel with a search input. If Explore is NOT in the sidebar,
    clicking Search navigates to /explore/ where the search input is on the page itself.
    """
    command = None

    def init(self):
        try:
            self.command = self.ig.account.create_command('hashtag scroll and like', 'processing')
            self.ig.account.add_cli("Starting hashtag scroll and like ...")
            self.hashtag_scroll_and_like()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback
            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_log(traceback.format_exc())
            self.ig.account.add_cli(f"Hashtag scroll and like failed: {str(e)}")

    def hashtag_scroll_and_like(self):
        hashtag = self._get_random_hashtag()

        if not hashtag:
            self.ig.account.add_cli("No hashtag available for this account's country, skipping")
            return

        self.ig.account.add_cli(f"Searching for hashtag: #{hashtag}")

        # Open search and type the hashtag
        self._search_for_hashtag(hashtag)

        # Wait for the posts grid to load
        self.ig.page.locator('a[href*="/p/"]').first.wait_for(state='visible', timeout=15000)
        self.ig.pause(3000, 5000)

        # Scroll and like loop
        like_count = 0
        rounds = random.randint(6, 8)

        for i in range(rounds):
            self.ig.page.mouse.wheel(0, random.randint(300, 600))
            self.ig.pause(3000, 6000)

            liked = self.try_open_and_like_post()
            if liked:
                like_count += 1

        self.ig.account.add_cli(f"Hashtag scroll and like finished. Liked {like_count}/{rounds} posts.")

    def _search_for_hashtag(self, hashtag):
        """
        Open search via sidebar and type the hashtag. After suggestions load,
        pick a random hashtag result from the dropdown.
        """
        search_input = self._open_search()

        if search_input:
            search_input.type(f'#{hashtag}', delay=random.randint(80, 180))

            # Wait for suggestions to load
            self.ig.account.add_cli("Waiting for hashtag suggestions ...")
            self.ig.pause(8000, 12000)

            # Pick a random hashtag from the suggestions
            self._click_random_hashtag_result()
        else:
            # Fallback: navigate directly
            self.ig.account.add_cli("Could not open search, navigating directly")
            url = f'https://www.instagram.com/explore/search/keyword/?q=%23{hashtag}'
            go_to_page(self.ig, url, 'hashtag page')

    def _open_search(self):
        """
        Click the Search icon in the sidebar. The behavior depends on whether
        Explore is also present:

        - Explore IS in sidebar: Search click opens a side panel with input
        - Explore NOT in sidebar: Search click navigates to /explore/ page with input

        Returns the search input element, or None on failure.
        """
        try:
            has_explore = (
                self.ig.page.locator('svg[aria-label="Explore"]').first.count() > 0
                and self.ig.page.locator('svg[aria-label="Explore"]').first.is_visible()
            )

            # Click the Search icon (always present)
            search_icon = self.ig.page.locator('svg[aria-label="Search"]').first
            search_icon.click(timeout=5000)

            if has_explore:
                # Side panel opens with search input
                self.ig.account.add_cli("Explore in sidebar — search panel opening")
                self.ig.pause(2000, 3000)

                search_input = self.ig.page.locator('input[aria-label="Search input"]').first
                if search_input.count() > 0 and search_input.is_visible():
                    return search_input

            else:
                # Navigates to /explore/ page
                self.ig.account.add_cli("No Explore in sidebar — navigating to /explore/")
                self.ig.pause(3000, 5000)

                # The input is inside a div[role="button"] that intercepts clicks,
                # so we click the parent div first to activate it, then return the input
                search_wrapper = self.ig.page.locator('div[role="button"]:has(input[placeholder="Search"])').first
                if search_wrapper.count() > 0 and search_wrapper.is_visible():
                    search_wrapper.click(timeout=5000)
                    self.ig.pause(1000, 2000)

                search_input = self.ig.page.locator('input[aria-label="Search input"]').first
                if search_input.count() == 0 or not search_input.is_visible():
                    search_input = self.ig.page.locator('input[placeholder="Search"]').first

                if search_input.count() > 0 and search_input.is_visible():
                    return search_input

        except Exception as e:
            self.ig.account.add_cli(f"Failed to open search: {str(e)}")

        return None

    def _click_random_hashtag_result(self):
        """
        From the search suggestions, find all hashtag links and click a random one.
        Hashtag results have href like /explore/tags/newyorkcity/
        """
        hashtag_links = self.ig.page.locator('a[href*="/explore/tags/"]').all()
        visible_links = [link for link in hashtag_links if link.is_visible()]

        if visible_links:
            chosen = random.choice(visible_links)
            href = chosen.get_attribute('href')
            self.ig.account.add_cli(f"Clicking random hashtag suggestion: {href}")

            # Use dispatch_event to bypass overlay elements intercepting pointer events
            chosen.dispatch_event('click')
            self.ig.pause(3000, 5000)
        else:
            self.ig.account.add_cli("No hashtag suggestions found, pressing Enter")
            self.ig.page.keyboard.press('Enter')
            self.ig.pause(3000, 5000)

    def _get_random_hashtag(self):
        """
        Pick a random city from the account's country and turn its name into a hashtag.
        Retries up to 10 times if the result is too short (< 4 chars).
        """
        country = self.ig.account.country

        if not country:
            self.ig.account.add_cli("Account has no country assigned")
            return None

        cities = list(
            City
            .select(City.name)
            .where(City.country == country)
        )

        if not cities:
            self.ig.account.add_cli(f"No cities found for country {country.name}")
            return None

        city = random.choice(cities)
        hashtag = self._name_to_hashtag(city.name)

        attempts = 0
        while len(hashtag) < 4 and attempts < 10:
            city = random.choice(cities)
            hashtag = self._name_to_hashtag(city.name)
            attempts += 1

        if len(hashtag) < 4:
            return None

        return hashtag

    def _name_to_hashtag(self, name):
        """
        Clean up a city name so it works as a hashtag.
        Strips non-alphanumeric characters and lowercases.
        """
        clean = re.sub(r"[^a-zA-Z0-9]", '', name)
        return clean.lower()

    def try_open_and_like_post(self):
        """
        Click a random visible post, like it, close the modal.
        """
        try:
            post_links = self.ig.page.locator('a[href*="/p/"]').all()
            visible_posts = [p for p in post_links if p.is_visible()]

            if not visible_posts:
                return False

            post = random.choice(visible_posts)
            post.click(timeout=5000)

            self.ig.pause(2000, 4000)

            liked = self.try_like()

            self.ig.pause(1000, 3000)

            self.ig.page.keyboard.press('Escape')
            self.ig.pause(2000, 4000)

            return liked

        except:
            try:
                self.ig.page.keyboard.press('Escape')
                self.ig.pause(1000, 2000)
            except:
                pass
            return False

    def try_like(self):
        """
        Find the heart icon and click its parent button element.
        """
        try:
            like_button = self.ig.page.locator('svg[aria-label="Like"]').first
            if like_button.count() > 0 and like_button.is_visible():
                like_button.locator('..').locator('..').click(timeout=3000)
                self.ig.pause(1000, 2000)
                return True
        except:
            pass
        return False