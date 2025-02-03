from time import sleep
import random


class BrowserBaseEvent:
    ig = None
    first_searched_user_locator = 'div.x9f619.xjbqb8w.x78zum5.x168nmei>div.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n'
    first_searched_user_alternative_locator = 'div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1pi30zi.x1swvt13.xwib8y2.x1y1aw1k.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.x1qjc9v5.x1oa3qoh.x1nhvcw1'
    search_input_locator = 'input[name="queryBox"][placeholder="Search"]'

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
        import re
        url = self.ig.page.url

        # Use regex to extract the thread_id after "/t/" and before a possible trailing slash
        match = re.search(r'/t/(\d+)', url)

        if match:
            # Return the thread_id if found
            return match.group(1)
        else:
            raise ValueError("Thread ID not found in URL")

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

    def go_to_lead_page(self, lead):
        try:
            self.go_to_lead_page_through_search(lead.username)
        except:
            self.go_to_lead_page_through_url(lead)

        self.ig.pause(5000, 5500)
        self.page_is_not_visible_handler()

    def search_for(self, phrase):
        try:
            search_button = self.ig.page.get_by_role("link", name="Search Search")
            search_button.wait_for(timeout=3000)
            search_button.click(timeout=3000)

        except:
            self.ig.page.get_by_role("link", name="Search").click(timeout=3000)
        self.ig.pause(3000, 3500)

        try:
            self.ig.page.get_by_placeholder("Search").fill(phrase)
        except:
            self.ig.page.locator("input[aria-label='Search input']").first.fill(phrase)


    def go_to_lead_page_through_search(self, username):
        self.search_for(username)
        self.ig.pause(4000, 5500)
        self.ig.page.locator(f'a[href*="/{username}/"]').first.click(timeout=3000)

    def go_to_lead_page_through_url(self, lead):
        self.ig.account.add_cli('Problem clicking on Lead button trying url intead')
        self.ig.page.goto(f'https://www.instagram.com/{lead.username}/')

    def click_on_send_message(self):
        try:
            self.ig.page.get_by_role("button", name="Message").click(timeout=3000)
        except:
            try:
                self.ig.account.add_cli("There's not Message button in lead's page, Trying options instead ... ")
                self.ig.page.get_by_role("button", name="Options").click()
                self.ig.pause(2500, 3500)
                self.ig.page.get_by_role("button", name="Send message").click(timeout=3000)
            except:
                raise Exception("There's not Message button in lead's page.")

    def sending_direct_by_search(self, lead):
        # Go to the lead page
        self.go_to_lead_page(lead)
        self.ig.pause(6000, 7000)
        # Send on click message in lead's page
        self.click_on_send_message()
        self.ig.pause(3000, 4000)

    def click_on_new_message(self):
        try:
            self.ig.page.get_by_role("button", name="New message").click(timeout=3000)
        except:
            try:
                self.ig.account.add_cli('There is no New message button clicking on Send message instead ...')
                self.ig.page.get_by_role("button", name="Send message").click(timeout=3000)
            except:
                try:
                    self.ig.account.add_cli('Problem clicking on Send message going to threads to try again ...')
                    self.go_to_threads()
                    self.ig.turn_on_notif()
                    self.ig.page.get_by_role("button", name="Send message").click(timeout=3000)
                except:
                    self.ig.page.get_by_role("button", name="New message").click(timeout=3000)

    def sending_direct_in_direct_page(self, lead):

        self.click_on_new_message()
        self.ig.pause(2000, 3000)

        try:
            self.ig.page.get_by_placeholder("Search").press_sequentially(lead.username, delay=120, timeout=7000)

        except:
            self.ig.account.add_cli('There is no locator with Search placeholder trying another method ...')
            self.ig.page.locator(self.search_input_locator).press_sequentially(lead.username, delay=120, timeout=6000)

        self.ig.pause(3000, 5000)

        try:
            self.ig.page.locator(self.first_searched_user_locator).first.click(timeout=3000)
        except:
            self.ig.account.add_cli('Trying second locator to click on first username ...')
            self.ig.page.locator(self.first_searched_user_alternative_locator).first.click(timeout=3000)

        self.ig.pause(1000, 3000)

        try:
            self.ig.page.get_by_role("button", name="Chat").click(timeout=3000)

        except:
            self.ig.account.add_cli('There is no Chat button ')

        self.ig.pause(3000, 4000)

    def sending_direct_by_thread_url_id(self, lead):
        pass

    def close_modal(self):
        try:
            self.ig.page.get_by_role("button", name="Close").click(timeout=3000)

        except Exception as e:
            self.ig.account.add_cli('Close modal button doesnt exists')

    def before_message_fill_part(self, lead):
        try:
            self.sending_direct_in_direct_page(lead)

            if not self.ig.is_visible_by_text(f'{lead.username} · Instagram'):
                raise Exception('Could not send direct in direct page trying by search ...')

        except Exception as e:
            self.ig.account.add_cli(str(e))
            self.close_modal()
            self.sending_direct_by_search(lead)

    def after_message_fill_part(self, lead):
        self.something_went_wrong_handler()
        self.not_every_one_can_message_this_account_handler(lead)
        self.send_more_messages_after_invite_accepted(lead)

        # Fill the text box with DM text
        self.ig.page.get_by_label("Message", exact=True).fill(lead.dm_text)
        self.ig.pause(2000, 3500)

        try:
            self.ig.page.get_by_role("button", name="Turn On", exact=True).click(timeout=2000)
        except:
            pass

        try:
            self.ig.page.get_by_role("button", name="Send", exact=True).click()
        except:
            raise Exception("There's no Send button")

        self.ig.pause(3000, 5000)

    def send_direct(self, lead, direct_url_id=None):

        if direct_url_id:
            self.ig.page.goto(f'https://www.instagram.com/direct/t/{direct_url_id}/')
            self.ig.pause(3000, 5000)

        else:
            self.before_message_fill_part(lead)

        self.after_message_fill_part(lead)

    def page_is_not_visible_handler(self):
        if self.ig.is_visible_by_text("this page isn't available") or self.ig.is_visible_by_text(
                "The link you followed may be broken, or the page may have been removed"):
            raise Exception("Sorry, this page isn't available")

    def something_went_wrong_handler(self):
        for _ in range(7):
            if self.ig.is_visible_by_text("Something went wrong. Please try again"):
                raise Exception("Something went wrong")

            self.ig.pause(700, 800)

    def not_every_one_can_message_this_account_handler(self, lead):
        if self.ig.is_visible_by_text("Not everyone can message this account"):

            lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)
            raise Exception("Not everyone can message this account")

    def send_more_messages_after_invite_accepted(self, lead):
        if self.ig.is_visible_by_text(
                "You can send more messages after your invite is accepted") or self.ig.is_visible_by_text(
                "You can send more messages after they accept"):

            lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)
            raise Exception("You can send more messages after your invite is accepted")
# Invite sent
# You can send more messages after your invite is accepted.

# azadsat7 · Instagram
# n
