from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
from script.models.Lead import Lead
from script.models.Command import performed_command_count
from peewee import fn
import random


class BrowserFollowPagesViaLocationEvent(InstagramMiddleware):
    """
    Warm-up event that follows pages from the leads table filtered by the account's country.

    Searches for the username via the sidebar Search icon to register search activity
    as an algorithm signal. Uses the same search approach as BrowserHashtagScrollAndLikeEvent.

    Daily limit: 1 follows per 24 hours, checked via command history.
    """
    command = None

    def init(self):
        try:
            if not self._can_follow_today():
                return

            self.command = self.ig.account.create_command('follow pages via location', 'processing')
            self.ig.account.add_cli("Starting follow pages via location ...")
            self.follow_page()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback
            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_log(traceback.format_exc())
            self.ig.account.add_cli(f"Follow pages via location failed: {str(e)}")

    def _can_follow_today(self):
        count = performed_command_count(self.ig.account, ['follow pages via location'], 24)

        if count >= 1:
            self.ig.account.add_cli(f'Already followed {count} pages today, skipping')
            return False

        return True

    def follow_page(self):
        lead = self._get_random_lead()

        if not lead:
            self.ig.account.add_cli("No lead found for this account's country, skipping")
            return

        username = lead.username
        self.ig.account.add_cli(f"Going to follow: {username}")

        # Search for the username via sidebar
        self._search_and_navigate(username)

        # Click the Follow button
        followed = self._click_follow()

        if not followed:
            self.ig.account.add_cli(f"Could not follow {username}, skipping suggested")
            return

        self.ig.account.add_cli(f"Successfully followed {username}")
        self.ig.pause(3000, 5000)

        # Follow one suggested account
        self._follow_suggested()

    def _get_random_lead(self):
        country = self.ig.account.country

        if not country:
            self.ig.account.add_cli("Account has no country assigned")
            return None

        lead = (
            Lead
            .select()
            .where(
                (Lead.country == country) &
                (Lead.screenshot_path.is_null())
            )
            .order_by(fn.Random())
            .first()
        )

        if not lead:
            self.ig.account.add_cli(f"No leads without screenshot for country {country.name}")

        return lead

    def _search_and_navigate(self, username):
        """
        Open search via sidebar, type the username, wait for results,
        then click the matching profile or navigate directly as fallback.
        """
        search_input = self._open_search()

        if search_input:
            search_input.type(username, delay=random.randint(80, 180))
            self.ig.pause(8000, 12000)

            # Try to click the matching profile from results
            clicked = self._click_profile_result(username)
            if clicked:
                self.ig.pause(3000, 4000)
                return

        # Fallback: navigate directly
        self.ig.account.add_cli("Navigating directly to profile")
        go_to_page(self.ig, f'https://www.instagram.com/{username}/', 'User page')
        self.ig.pause(3000, 4000)

    def _open_search(self):
        """
        Click the Search icon in the sidebar.

        - If Explore is also in sidebar: side panel opens with input
        - If Explore is NOT in sidebar: navigates to /explore/ with input on page

        Returns the search input element, or None on failure.
        """
        try:
            has_explore = (
                self.ig.page.locator('svg[aria-label="Explore"]').first.count() > 0
                and self.ig.page.locator('svg[aria-label="Explore"]').first.is_visible()
            )

            # Click Search icon (always present)
            search_icon = self.ig.page.locator('svg[aria-label="Search"]').first
            search_icon.click(timeout=5000)

            if has_explore:
                # Side panel opens
                self.ig.account.add_cli("Explore in sidebar — search panel opening")
                self.ig.pause(2000, 3000)

                search_input = self.ig.page.locator('input[aria-label="Search input"]').first
                if search_input.count() > 0 and search_input.is_visible():
                    return search_input

            else:
                # Navigates to /explore/
                self.ig.account.add_cli("No Explore in sidebar — navigating to /explore/")
                self.ig.pause(3000, 5000)

                # The input is inside a div[role="button"] that intercepts clicks,
                # so we click the parent div first to activate it
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

    def _click_profile_result(self, username):
        """
        Try to click a profile link matching the username from search results.
        """
        try:
            profile_link = self.ig.page.locator(f'a[href="/{username}/"]').first
            if profile_link.count() > 0 and profile_link.is_visible():
                profile_link.click(timeout=5000)
                return True
        except:
            pass

        return False

    def _click_follow(self):
        try:
            follow_button = self.ig.page.get_by_role("button", name="Follow")
            if follow_button.count() > 0 and follow_button.first.is_visible():
                follow_button.first.click(timeout=5000)
                self.ig.pause(2000, 4000)
                return True
        except:
            pass

        self.ig.account.add_cli("Follow button not found or not clickable")
        return False

    def _follow_suggested(self):
        try:
            follow_buttons = self.ig.page.query_selector_all('div[role="button"]:has-text("Follow")')
            self.ig.account.add_cli(f"Found {len(follow_buttons)} suggested follow buttons")

            if not follow_buttons:
                return

            button = random.choice(follow_buttons)
            button.click(timeout=4000)
            self.ig.pause(2000, 4000)

            self.ig.account.add_cli("Followed 1 suggested account")

        except Exception as e:
            self.ig.account.add_cli(f"Could not follow suggested: {str(e)}")