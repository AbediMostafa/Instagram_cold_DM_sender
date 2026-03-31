from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
from script.models.City import City
import random
import re


class BrowserHashtagScrollAndLikeEvent(InstagramMiddleware):
    """
    Warm-up event that searches for a hashtag on Instagram and likes random posts.

    Hashtags are generated dynamically from city names in the database, filtered by the
    account's country. For example if the account belongs to the US and we have a city
    called "New York City", the hashtag becomes #newyorkcity. This way we don't need
    a hardcoded list and every country gets relevant hashtags automatically once cities
    are scraped.

    If the account has no country assigned, the event is skipped entirely.
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

        url = f'https://www.instagram.com/explore/search/keyword/?q=%23{hashtag}'

        self.ig.account.add_cli(f"Navigating to hashtag: #{hashtag}")
        go_to_page(self.ig, url, 'hashtag page')

        # Wait until at least one post link shows up
        self.ig.page.locator('a[href*="/p/"]').first.wait_for(state='visible', timeout=15000)
        self.ig.pause(3000, 5000)

        like_count = 0
        rounds = random.randint(6, 8)

        for i in range(rounds):
            self.ig.page.mouse.wheel(0, random.randint(300, 600))
            self.ig.pause(3000, 6000)

            liked = self.try_open_and_like_post()
            if liked:
                like_count += 1

        self.ig.account.add_cli(f"Hashtag scroll and like finished. Liked {like_count}/{rounds} posts.")

    def _get_random_hashtag(self):
        """
        Pick a random city from the account's country and turn its name into a hashtag.

        We keep trying up to 10 times if the first pick results in something too short
        (less than 4 chars). City names like "AD" or "ML" don't make good hashtags,
        so we skip those.
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

        # Try picking a city whose name makes a decent hashtag
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

        Strips out everything that isn't a letter or digit, then lowercases it.
        Examples:
            "New York City"  -> "newyorkcity"
            "St. Charles"    -> "stcharles"
            "Davio's Philly" -> "daviosphilly"
            "JFK Plaza / Love Park" -> "jfkplazalovepark"
        """
        clean = re.sub(r"[^a-zA-Z0-9]", '', name)
        return clean.lower()

    def try_open_and_like_post(self):
        """
        Click a random visible post, like it, close the modal.
        Returns True if we managed to like, False if anything went wrong.
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

            # Stay on the post for a bit to look natural
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
        Find the heart icon and click it. We go two levels up from the SVG
        to reach the actual clickable button element.
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