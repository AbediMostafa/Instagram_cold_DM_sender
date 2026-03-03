import sys
import os
import random
import string
import re
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.extra.base.BasePlaywright import BasePlaywright
from script.models.Template import get_next
from script.models.Account import Account
from script.extra.helper import generate_random_word
from script.extra.actions.scroll_and_like.ScrollAndLikeContext import ScrollAndLikeContext
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent

months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


class AccountMakerMailTd:
    name_username = None
    account = None
    email = None
    username = None
    name = None
    month = None
    day = None
    year = None
    ig = None
    page1 = None
    code = None

    def __init__(self):
        self.get_account_info()
        self.create_account()

        self.ig = BasePlaywright(self.account)
        self.ig.init()

        try:
            self.ig.go_to_instagram()
            self.allow_cookies()

            self.go_to_tmp_mail()
            self.ig.page.bring_to_front()

            self.start()

        except Exception as e:
            self.ig.account.add_cli(f'Deleting account, reason {str(e)}')
            self.ig.account.delete_instance()

    def get_account_info(self):
        self.name_username = get_next('name-username')
        self.username = self.name_username.text
        print(f'Username : {self.name_username.text}')

        self.name = self.name_username.caption
        self.month = random.choice(months)
        self.day = random.randint(1, 28)
        self.year = random.randint(1980, 2005)

        self.modify_username()

    def create_account(self):
        self.account = Account.create(
            username=self.username,
            password=generate_random_word(),
            name=self.name,
            username_changed=1
        )

        self.account.add_cli(f'Created account with username {self.account.username}')

    def start(self):
        self.ig.account.add_cli('Starting to create new account ... ')
        self.ig.pause(3000, 4000)

        # Click on new account
        try:
            self.ig.page.get_by_role("link", name="Create new account").click(timeout=4000)
            self.ig.account.add_cli('Create new account clicked ....')

        except Exception as e:
            self.ig.account.add_cli('Create new account first method failed trying second method ...')
            self.ig.page.locator("a[aria-label='Create new account']").click(timeout=4000)

        # Fill email
        self.ig.pause(8000, 8500)
        self.fill_email()
        self.ig.pause(2000, 3000)

        # while self.ig.is_visible_by_text('Please enter a valid mobile number'):
        #     self.ig.account.add_cli(f'Please enter a valid mobile number or email address')
        #     self.modify_username_and_save()
        #     self.fill_email()
        #     self.ig.pause(2000, 3000)

        # Fill Password
        self.ig.pause(1000, 2000)
        self.ig.account.add_cli('Filling password ...')
        self.ig.account.add_cli(self.ig.account.password)
        self.ig.page.get_by_label("Password").press_sequentially(self.ig.account.password, delay=100, timeout=4500)

        # Select month
        self.ig.pause(1000, 2000)
        self.ig.account.add_cli('Clicking on month combo box ...')
        self.ig.page.get_by_role("combobox", name="Select Month").click(timeout=3000)
        self.ig.pause(1000, 1500)
        self.ig.page.get_by_text(self.month, exact=True).click(timeout=3000)
        self.ig.pause(1000, 2000)

        # Select Day
        self.ig.account.add_cli('Clicking on Day combo box ...')
        self.ig.page.get_by_role("combobox", name="Select Day").click(timeout=3000)
        self.ig.pause(1000, 1500)
        day_value = str(self.day).strip()
        locator = self.ig.page.get_by_role("option", name=day_value, exact=True)
        locator.wait_for()
        locator.click(timeout=3000)
        self.ig.pause(1000, 2000)

        # Select Year
        self.ig.account.add_cli('Clicking on Day combo box ...')
        self.ig.page.get_by_role("combobox", name="Select Year").click(timeout=3000)
        self.ig.pause(1000, 1500)
        year_value = str(self.year).strip()
        locator = self.ig.page.get_by_role("option").filter(has_text=year_value)
        locator.wait_for()
        locator.click(timeout=3000)
        self.ig.pause(1000, 2000)

        # Fill Name
        self.ig.account.add_cli('Filling Name ...')
        self.ig.page.get_by_label("Full name").press_sequentially(self.name, delay=100, timeout=4500)
        self.ig.pause(1000, 2000)

        # Fill username
        self.ig.account.add_cli('Filling username ...')
        self.ig.page.get_by_label("Username").fill('')
        self.ig.pause(2000, 2500)
        self.ig.page.get_by_label("Username").fill('')
        self.ig.pause(1000, 1500)
        self.ig.page.get_by_label("Username").press_sequentially(self.username, delay=100, timeout=4500)
        self.ig.pause(1000, 2000)

        self.ig.page.get_by_role("button", name="Submit").click(timeout=4500)

        self.ig.pause(8000, 9000)

        self.extract_code()
        self.ig.page.bring_to_front()

        # Fill Code
        self.ig.pause(1000, 2000)
        self.ig.account.add_cli('Filling Code ...')
        self.ig.page.get_by_label("Confirmation code").press_sequentially(self.code, delay=100, timeout=4500)
        self.ig.pause(1000, 2000)
        self.ig.page.get_by_role("button", name="Continue").click(timeout=4500)
        self.ig.pause(13000, 15000)

        for i in range(4):
            self.change_how_we_manage_data()
            self.updated_to_our_terms()
            self.confirm_you_are_human_to_use_your_account()
            self.an_error_occurred_during_your_registration()
            self.allow_the_use_of_cookies()
            self.ig.pause(1000, 2000)

        self.ig.go_to_instagram()
        self.save_session()
        self.follow_suggested()

        ScrollAndLikeContext(self.ig).fire()
        self.ig.pause(1000, 2000)
        BrowserChangeAvatarEvent(self.ig).fire()

    def extract_code(self):
        self.page1.bring_to_front()

        email_element = self.page1.locator("div.mail-item").first
        text = email_element.inner_text()

        # Extract 6 digit code
        match = re.search(r'\b(\d{6})\b', text)
        self.code = match.group(1) if match else None

        print(f'Code : {self.code}')

    def fill_email(self):
        self.ig.account.add_cli('Filling email ...')
        self.ig.page.get_by_label("Mobile number or email").press_sequentially(self.email, delay=100,
                                                                               timeout=4500)

    def modify_username(self):
        char = random.choice(string.ascii_lowercase)

        pos = random.randint(1, len(self.username) - 1)  # not first, not last
        self.username = self.username[:pos] + char + self.username[pos:]

    def modify_username_and_save(self):
        self.modify_username()
        self.ig.account.username = self.username
        self.ig.account.save()

    def allow_cookies(self):
        for i in range(3):
            try:
                try:
                    self.ig.page.locator('button', has_text='Allow All Cookies').click(timeout=1500)
                except:
                    self.ig.page.locator('button', has_text='Allow all cookies').click(timeout=1500)

                return True
            except Exception as e:
                pass

    def go_to_tmp_mail(self):
        from urllib.parse import urlparse
        import time

        print('Going to tmp mail')
        self.page1 = self.ig.context.new_page()

        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            attempt += 1
            try:
                print(f"Opening mail.td (Attempt {attempt})")
                self.page1.goto("https://mail.td/", wait_until="domcontentloaded", timeout=10000)

                self.ig.pause(4000, 5000)

                current_url = self.page1.url

                if "mail.td" in current_url:
                    print("Correct domain loaded.")
                    break
                else:
                    print(f"Redirected to ad page: {current_url}")
                    self.page1.close()
                    self.page1 = self.ig.context.new_page()

            except Exception as e:
                print(f"Error going to Mail.td: {str(e)}")

        else:
            raise Exception("Failed to load mail.td after 3 attempts")

        # بررسی کپچا
        if self.ig.is_visible_by_text('Verify you are human') or \
                self.ig.is_visible_by_text('temp-mail.org needs to review the security'):
            raise Exception('Verify you are human')

        self.ig.pause(2000, 3000)
        self.ig.account.add_cli('Mail.td Loaded ...')

        self.page1.get_by_role("link", name="Random Email Address").click(timeout=4000)
        self.ig.pause(2000, 3000)

        current_url = self.page1.url
        path = urlparse(current_url).path
        self.email = path.split("/")[-1]

        self.ig.account.add_cli(f"Extracted email: {self.email}")

    def change_how_we_manage_data(self):
        if self.ig.is_visible_by_text('Changes to How We Manage Data'):
            self.ig.page.get_by_role("button", name="Next").click(timeout=4500)
            self.ig.pause(3000, 4000)

    def updated_to_our_terms(self):
        if self.ig.is_visible_by_text('Updates to Our Terms'):
            self.ig.page.get_by_role("button", name="Agree to Terms").click(timeout=4500)
            self.ig.pause(3000, 4000)

    def save_session(self):
        self.ig.account.add_cli('Saving session ...')

        storage_state = self.ig.page.context.storage_state()
        storage_state_json = json.dumps(storage_state)
        self.ig.account.save_session(storage_state_json)

    def confirm_you_are_human_to_use_your_account(self):
        if self.ig.is_visible_by_text("Confirm you're human"):
            self.ig.pause(1800, 3000)
            raise Exception("Confirm you're human")

    def an_error_occurred_during_your_registration(self):
        if self.ig.is_visible_by_text("An error occurred during your registration"):
            self.ig.pause(1800, 3000)
            raise Exception("An error occurred during your registration")

    def allow_the_use_of_cookies(self):
        if self.ig.is_visible_by_text('Allow the use of cookies'):
            try:
                self.ig.page.locator('button', has_text='Allow All Cookies').click(timeout=2000)
            except Exception as e:
                self.ig.page.locator('button', has_text='Allow all cookies').click(timeout=2000)
            self.ig.pause(3000, 4000)

    def follow_suggested(self):
        if self.ig.is_visible_by_text('Find friends and accounts you like'):
            print('Find friends and accounts you like')

            for _ in range(2):
                try:
                    self.ig.page.get_by_role("button", name="Next").first.click(timeout=3000)
                except Exception as e:
                    print(str(e))

                self.ig.pause(3000, 5000)


account = AccountMakerMailTd()
# An error occurred during your registration. Please try again.
