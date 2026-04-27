from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.helper import go_to_page
import random


class BrowserScrollAndLikeEvent(InstagramMiddleware):
    """
    Event class for scrolling through the Instagram feed, liking posts,
    and watching stories to simulate natural user behavior.
    """
    command = None

    def init(self):
        """
        Main entry point. Creates a command record, then runs story watching
        followed by scroll and like actions.
        """
        try:
            self.command = self.ig.account.create_command('scroll and like', 'processing')
            self.ig.account.add_cli("Starting scroll and like ...")
            self.turn_on_notif()

            if random.random() < 0.3:
                self.watch_stories()

            self.scroll_and_like()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback

            self.command.update_cmd('state', 'fail')
            self.ig.account.add_log(traceback.format_exc())
            self.ig.account.add_cli(f"Scroll and like failed: {str(e)}")

    def watch_stories(self):
        """
        Watches a random number of unseen stories from the story bar on the home feed.
        First checks if any unseen stories exist. If they do, clicks the first one to open
        the story viewer, waits a random duration on each story, then moves to the next one.
        After watching the desired number, closes the story viewer.
        """
        try:
            # Look for unseen story items in the story bar
            unseen_selector = 'div[aria-label*="Story by"][aria-label*="not seen"][role="button"]'
            unseen_stories = self.ig.page.locator(unseen_selector)

            self.ig.pause(2000, 3000)

            unseen_count = unseen_stories.count()

            if unseen_count == 0:
                self.ig.account.add_cli("No unseen stories found, skipping story watching")
                return

            # Pick how many stories to watch (5 to 8), but cap it at available count
            target_count = min(random.randint(5, 8), unseen_count)
            self.ig.account.add_cli(f"Found {unseen_count} unseen stories, will watch {target_count}")

            # Click the first unseen story to open the story viewer
            unseen_stories.first.click(timeout=5000)
            self.ig.pause(2000, 3000)

            for i in range(target_count):
                # Wait a random time between 7 and 10 seconds to simulate actually viewing the story
                watch_duration = random.randint(7000, 10000)
                self.ig.account.add_cli(f"Watching story {i + 1}/{target_count} for {watch_duration}ms")
                self.ig.pause(watch_duration, watch_duration + 500)

                # If this is not the last story we want to watch, move to the next one
                if i < target_count - 1:
                    self.go_to_next_story()

            # Done watching, close the story viewer
            self.close_story_viewer()
            self.ig.pause(1500, 2500)
            self.ig.account.add_cli(f"Finished watching {target_count} stories")

        except Exception as e:
            self.ig.account.add_cli(f"Story watching failed: {str(e)}")
            # Try to close the story viewer in case it is still open
            self.close_story_viewer()

    def go_to_next_story(self):
        """
        Moves to the next story inside the story viewer. Tries clicking the Next button first.
        If the button is not found, falls back to pressing the ArrowRight key.
        """
        try:
            next_button = self.ig.page.locator('button[aria-label="Next"]')
            if next_button.count() > 0 and next_button.first.is_visible():
                next_button.first.click(timeout=3000)
                self.ig.pause(500, 1000)
                return
        except:
            pass

        # Fallback: use keyboard arrow right to advance
        try:
            self.ig.page.keyboard.press('ArrowRight')
            self.ig.pause(500, 1000)
        except:
            self.ig.account.add_cli("Could not move to next story")

    def close_story_viewer(self):
        """
        Closes the story viewer overlay. Tries the close button first,
        then falls back to pressing Escape if the button is not available.
        """
        try:
            # Instagram story viewer typically has a close button with svg or specific role
            close_button = self.ig.page.locator('button:has(svg[aria-label="Close"])').first
            if close_button.count() > 0 and close_button.is_visible():
                close_button.click(timeout=3000)
                return
        except:
            pass

        # Fallback: press Escape to close the overlay
        try:
            self.ig.page.keyboard.press('Escape')
        except:
            self.ig.account.add_cli("Could not close story viewer")

    def scroll_and_like(self):

        for i in range(random.randint(4, 12)):
            self.ig.page.mouse.wheel(0, random.randint(650, 700))
            self.ig.pause(2000, 4000)

            if random.random() < 0.2:
                self.ig.page.reload()
                self.ig.pause(3000, 4000)
                self.turn_on_notif()

            if random.random() < 0.3:
                self.try_like()

    def try_like(self):

        selectors = [
            'div[style*="max-width"] section div[role="button"]:has(svg[aria-label="Like"]) >> nth=0',
        ]

        for selector in selectors:
            try:
                element = self.ig.page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click(timeout=3000)
                    self.ig.pause(1000, 2000)
            except:
                continue

        return False

    def turn_on_notif(self):
        import re
        if self.ig.is_visible_by_text('Turn On notif'):
            try:
                self.ig.page.get_by_role('button', name=re.compile(r'Turn On', re.IGNORECASE)).click()
                self.ig.pause(4000, 5000)
            except:
                self.ig.account.add_cli("Turn On doesn't exists")
                pass