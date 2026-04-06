from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
from script.models.Location import Location
from script.models.City import City
from peewee import fn
import random


class BrowserLocationScrollAndLikeEvent(InstagramMiddleware):
    """
    Warm-up event that scrolls through a real Instagram location page and likes random posts.

    Instead of using a hardcoded list of locations, this picks a random location from
    the database that belongs to the account's assigned country. If the account has no
    country set, the whole thing is skipped to avoid warming up in the wrong region.
    """
    command = None

    def init(self):
        try:
            self.command = self.ig.account.create_command('location scroll and like', 'processing')
            self.ig.account.add_cli("Starting location scroll and like ...")
            self.location_scroll_and_like()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback
            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_log(traceback.format_exc())
            self.ig.account.add_cli(f"Location scroll and like failed: {str(e)}")

    def location_scroll_and_like(self):
        location = self._get_random_location()

        if not location:
            self.ig.account.add_cli("No location found for this account's country, skipping")
            return

        # Build the URL and go to the "recent" tab so we get fresh posts
        url = f'https://www.instagram.com/explore/locations/{location.location_id}/{location.slug}/recent/'

        self.ig.account.add_cli(f"Navigating to location: {location.name}")
        go_to_page(self.ig, url, 'location page')

        # Give the page a moment to render the post grid
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

        self.ig.account.add_cli(f"Location scroll and like finished. Liked {like_count}/{rounds} posts.")

    def _get_random_location(self):
        """
        Grab a random location from the DB that belongs to the account's country.
        We first collect all city IDs for that country, then pick a random location
        from any of those cities.
        Returns None if the account has no country or no locations exist yet.
        """
        country = self.ig.account.country

        if not country:
            self.ig.account.add_cli("Account has no country assigned")
            return None

        city_ids = [c.id for c in City.select(City.id).where(City.country == country)]

        if not city_ids:
            self.ig.account.add_cli(f"No cities found for country {country.name}")
            return None

        location = (
            Location
            .select()
            .where(Location.city.in_(city_ids))
            .order_by(fn.Random())
            .first()
        )

        return location

    def try_open_and_like_post(self):
        """
        Click on a random visible post in the grid, like it, then close the modal.
        Returns True if we actually liked something, False otherwise.
        """
        try:
            post_links = self.ig.page.locator('a[href*="/p/"]').all()
            visible_posts = [p for p in post_links if p.is_visible()]

            if not visible_posts:
                return False

            post = random.choice(visible_posts)
            post.click(timeout=5000)

            # Let the post modal fully load before trying to like
            self.ig.pause(2000, 4000)

            liked = self.try_like()

            # Hang around a bit so it looks like we're actually viewing the post
            self.ig.pause(1000, 3000)

            self.ig.page.keyboard.press('Escape')
            self.ig.pause(2000, 4000)

            return liked

        except:
            # Something went wrong, just close the modal and move on
            try:
                self.ig.page.keyboard.press('Escape')
                self.ig.pause(1000, 2000)
            except:
                pass
            return False

    def try_like(self):
        """
        Find the Like button (the heart SVG) and click its parent element.
        Returns True if the click went through.
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