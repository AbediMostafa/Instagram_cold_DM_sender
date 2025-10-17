from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.helper import go_to_page
import time
import random
import re
import os
from datetime import datetime


class BrowserRegisterEmailEvent(InstagramMiddleware):
    """
    Event class for executing email registration on Instagram
    """
    command = None
    _debug_log_path = None
    _code_source = None

    def init(self):
        """
        Initialize and execute the email registration process
        """
        try:
            self.command = self.ig.account.create_command('register email', 'processing')
            self.ig.account.add_cli("Starting email registration process...")
            self._navigate_to_contact_info()
            self._analyze_contact_info()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            import traceback

            self.command.update_cmd('state', 'fail')
            self.ig.account.add_log(traceback.format_exc())
            self.ig.account.add_cli(f"Email registration failed: {str(e)}")
        finally:
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")
            self.ig.pause(3000, 4000)

    def _navigate_to_contact_info(self):
        """Navigate through Instagram to reach contact info page"""
        steps = [
            ("profile", self._click_on_profile, self._is_in_profile_page),
            ("options", self._click_on_options, self._is_options_menu_open),
            ("settings", self._click_on_settings_and_privacy, self._is_settings_page_open),
            ("accounts center", self._click_on_accounts_center, self._is_accounts_center_page_open),
            ("personal details", self._click_on_personal_details, self._is_personal_details_page_open),
            ("contact info", self._click_on_contact_info, self._is_contact_info_page_open)
        ]

        for step_name, click_func, verify_func in steps:
            try:
                self.ig.account.add_cli(f"Navigating to {step_name}...")
                click_func()
                self.ig.pause(6000, 8000)

                if not verify_func():
                    self.ig.account.add_cli(f"Failed to reach {step_name}")
                    raise Exception(f"Failed to reach {step_name}")
            except Exception as e:
                self.ig.account.add_cli(f"Error in {step_name}: {str(e)}")
                raise

    def _click_on_profile(self):
        """Click on profile using different methods"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                profile_selectors = [
                    'span:has-text("Profile")',
                    f'a[href="/{self.ig.account.username}/"]',
                    f'img[alt*="{self.ig.account.username}\'s profile picture"]',
                    'a[role="link"]:has-text("Profile")'
                ]

                for selector in profile_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=8000)
                        self.ig.page.wait_for_load_state("domcontentloaded", timeout=15000)
                        self.ig.pause(2000, 3000)
                        if self._is_in_profile_page():
                            return True
                    except Exception as e:
                        continue

                raise Exception("Could not access profile page with any method")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking profile")

        raise Exception("Failed to click on profile after 3 attempts.")

    def _is_in_profile_page(self):
        """Check if we are in profile page"""
        current_url = self.ig.page.url
        url_check = f"/{self.ig.account.username}/" in current_url
        text_check = (
                self.ig.is_visible_by_text("posts") or
                self.ig.is_visible_by_text("followers") or
                self.ig.is_visible_by_text("following") or
                self.ig.is_visible_by_text("Edit profile")
        )
        return url_check or text_check

    def _click_on_options(self):
        """Click on Options button"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                options_selectors = [
                    'svg[aria-label="Options"]',
                    'div[role="button"]:has(svg[aria-label="Options"])',
                    'svg:has(title:text("Options"))',
                    'button:has(svg[aria-label="Options"])'
                ]

                for selector in options_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=10000)
                        self.ig.pause(2000, 3000)
                        if self._is_options_menu_open():
                            return True
                    except:
                        continue

                raise Exception("Could not click on Options button")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking options")

        raise Exception("Failed to click on options after 3 attempts.")

    def _is_options_menu_open(self):
        """Check if options menu is opened"""
        menu_indicators = ["Settings and privacy", "Your activity", "Archive", "QR code"]
        return any(self.ig.is_visible_by_text(indicator) for indicator in menu_indicators)

    def _click_on_settings_and_privacy(self):
        """Click on Settings and privacy button"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                settings_selectors = [
                    'button:has-text("Settings and privacy")',
                    'button[tabindex="0"]:has-text("Settings and privacy")',
                    '[role="button"]:has-text("Settings and privacy")'
                ]

                for selector in settings_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=10000)
                        self.ig.pause(2000, 3000)
                        if self._is_settings_page_open():
                            return True
                    except:
                        continue

                raise Exception("Could not click on Settings and privacy")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking settings and privacy")

        raise Exception("Failed to click on settings and privacy after 3 attempts.")

    def _is_settings_page_open(self):
        """Check if settings page is opened"""
        current_url = self.ig.page.url
        url_check = "accounts/edit" in current_url
        text_check = (self.ig.is_visible_by_text("Settings") or
                      self.ig.is_visible_by_text("Edit profile"))
        return url_check and text_check

    def _click_on_accounts_center(self):
        """Click on Accounts Center"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                accounts_center_selectors = [
                    'span:has-text("See more in Accounts Center")',
                    'a[href*="accountscenter.instagram.com"]',
                    'a:has-text("See more in Accounts Center")'
                ]

                for selector in accounts_center_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=15000)
                        self.ig.page.wait_for_url("*accountscenter.instagram.com*", timeout=10000)
                        self.ig.page.wait_for_load_state("domcontentloaded", timeout=15000)
                        self.ig.pause(3000, 4000)
                        if self._is_accounts_center_page_open():
                            return True
                    except:
                        continue

                current_url = self.ig.page.url
                if "accountscenter.instagram.com" in current_url:
                    if self._is_accounts_center_page_open():
                        return True

                raise Exception("Could not click on Accounts Center")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking accounts center")

        raise Exception("Failed to click on accounts center after 3 attempts.")

    def _is_accounts_center_page_open(self):
        """Check if accounts center page is opened"""
        try:
            current_url = self.ig.page.url
            url_check = "accountscenter.instagram.com" in current_url

            if url_check:
                for attempt in range(3):
                    text_check = (self.ig.is_visible_by_text("Accounts Center") or
                                  self.ig.is_visible_by_text("Personal details") or
                                  self.ig.is_visible_by_text("Account settings") or
                                  self.ig.is_visible_by_text("Privacy"))
                    if text_check:
                        return True
                    self.ig.pause(1000, 2000)
                return True

            return False
        except Exception as e:
            return False

    def _click_on_personal_details(self):
        """Click on Personal details"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                personal_details_selectors = [
                    'span:has-text("Personal details")',
                    'a[href="/personal_info/"]',
                    'a:has-text("Personal details")'
                ]

                for selector in personal_details_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=10000)
                        self.ig.pause(2000, 3000)
                        if self._is_personal_details_page_open():
                            return True
                    except:
                        continue

                raise Exception("Could not click on Personal details")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking personal details")

        raise Exception("Failed to click on personal details after 3 attempts.")

    def _is_personal_details_page_open(self):
        """Check if personal details page is opened"""
        current_url = self.ig.page.url
        url_check = "accountscenter.instagram.com/personal_info/" in current_url
        text_check = self.ig.is_visible_by_text("Personal details")
        return url_check and text_check

    def _click_on_contact_info(self):
        """Click on Contact info"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                contact_info_selectors = [
                    'div[role="listitem"]:has-text("Contact info")',
                    '[role="button"]:has-text("Contact info"):not(:has-text("Account ownership")):not(:has-text("Birthday"))'
                ]

                for selector in contact_info_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=10000)
                        self.ig.pause(2000, 3000)
                        if self._is_contact_info_page_open():
                            return True
                    except:
                        continue

                raise Exception("Could not click on Contact info")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking contact info")

        raise Exception("Failed to click on contact info after 3 attempts.")

    def _is_contact_info_page_open(self):
        """Check if contact info page is opened"""
        current_url = self.ig.page.url
        url_check = ("contact_points" in current_url or "contact_info" in current_url)
        text_check = (self.ig.is_visible_by_text("Contact information") or
                      self.ig.is_visible_by_text("Add new contact"))
        return url_check and text_check

    def _analyze_contact_info(self):
        """Analyze contact information and determine next action"""
        if self._has_verified_email():
            self.ig.account.add_cli("Verified email found")
            self.ig.account.is_verify = 1
            self.ig.account.save()
            return

        if self._has_verified_phone():
            self.ig.account.add_cli("Verified phone found")
            self.ig.account.is_verify = 1
            self.ig.account.save()
            return

        if self._has_only_pending_phone():
            self.ig.account.add_cli("Only pending phone found")
        else:
            self.ig.account.add_cli("No verified contacts found")

        self._get_temp_email_and_add()

    def _get_temp_email_and_add(self):
        """Get temp email first, then add it to the form"""
        self.ig.account.add_cli("Getting temp email...")
        self._get_temp_email()

        self.ig.account.add_cli("Adding email to Instagram...")
        self._add_new_email()

    def _get_temp_email(self):
        """Open temp mail in new tab and get email address"""
        try:
            self.ig.account.add_cli("Opening temp mail...")
            self.page1 = self.ig.browser.new_page()
            self.page1.on("response", self._page1_response_fetcher)

            self.page1.goto("https://temp-mail.org/en/", wait_until="domcontentloaded", timeout=15000)
            self.ig.pause(3000, 5000)

            if self._check_human_verification_temp_mail():
                raise Exception('Human verification (Cloudflare) detected on temp mail')

            max_attempts = 8
            for attempt in range(max_attempts):
                if hasattr(self, 'email') and self.email:
                    self.ig.account.add_cli(f"Got temp email: {self.email}")
                    break
                self.ig.pause(1500, 2500)

            if not hasattr(self, 'email') or not self.email:
                raise Exception("Could not get temp email after waiting")

            self.ig.page.bring_to_front()

        except Exception as e:
            self.ig.account.add_cli(f"Error getting temp email: {str(e)}")
            try:
                self.ig.page.bring_to_front()
            except:
                pass
            raise

    def _page1_response_fetcher(self, response):
        """Handle responses from temp mail page"""
        try:
            if "web2.temp-mail.org/mailbox" in response.url:
                json_data = response.json()
                self.email = json_data['mailbox']

            if "web2.temp-mail.org/messages" in response.url:
                json_data = response.json()
                if not json_data.get('messages'):
                    return

                message = json_data['messages'][0]
                subject = message.get('subject', '')
                body = message.get('body', '')

                self._last_email_subject = subject
                self._last_email_body = body

                self.ig.account.add_cli("Email received via API")
                self._debug_log(section="api_email_received", text=f"SUBJECT: {subject}\nBODY: {body[:500]}")

                match = re.search(r'\b\d{6}\b', subject)
                if match:
                    candidate_code = match.group()
                    if self._is_likely_verification_code(candidate_code, subject):
                        self.code = candidate_code
                        self._code_source = "API_SUBJECT"
                        self.ig.account.add_cli(f"[API-SUBJECT] Found code: {self.code}")
                        self._debug_log_code_and_html(source="api_response_subject")
                        return

                instagram_patterns = [
                    r'(?:confirmation|verify|security|تأیید).*?(?:code|کد)[:\s]*[‏\u200f]*(\d{6})',
                    r'(?:enter|وارد کنید).*?(?:this\s*)?(?:code|کد)[:\s]*[‏\u200f]*(\d{6})',
                    r'Instagram.*?[:\s]*[‏\u200f]*(\d{6})',
                ]

                for pattern in instagram_patterns:
                    match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                    if match:
                        candidate_code = match.group(1)
                        if self._is_likely_verification_code(candidate_code, body):
                            self.code = candidate_code
                            self._code_source = "API_BODY_PATTERN"
                            self.ig.account.add_cli(f"[API-BODY-PATTERN] Found code: {self.code}")
                            self._debug_log_code_and_html(source="api_response_body_pattern")
                            return

                standalone_pattern = r'(?<![a-zA-Z0-9/#])(\d{6})(?![a-zA-Z0-9/#])'
                matches = re.findall(standalone_pattern, body)

                for candidate_code in matches:
                    if self._is_likely_verification_code(candidate_code, body):
                        self.code = candidate_code
                        self._code_source = "API_BODY_STANDALONE"
                        self.ig.account.add_cli(f"[API-BODY-STANDALONE] Found code: {self.code}")
                        self._debug_log_code_and_html(source="api_response_body_standalone")
                        return

        except Exception as e:
            self.ig.account.add_cli(f"Error processing temp mail response: {str(e)}")

    def _check_human_verification_temp_mail(self):
        """Check if human verification is required in temp mail tab"""
        verification_indicators = [
            'Verify you are human',
            'temp-mail.org needs to review the security',
            'Just a moment',
            'cf-challenge-running',
            'Cloudflare',
            'Ray ID:',
            'Performance & security by Cloudflare'
        ]

        try:
            page_text = self.page1.locator('body').inner_text()
            is_verification = any(indicator in page_text for indicator in verification_indicators)

            if is_verification:
                self._debug_log(section="human_verification_detected", text=page_text[:500])
                self.ig.account.add_cli("WARNING: Cloudflare Challenge detected!")

            return is_verification
        except:
            return False

    def _add_new_email(self):
        """Complete email addition flow"""
        steps = [
            ("Add new contact", self._click_add_new_contact),
            ("Add email", self._click_add_email),
            ("Fill email", self._fill_email_form),
            ("Check agreement", self._check_agreement_checkbox),
            ("Click Next", self._click_next_button),
            ("Wait for code", self._wait_for_verification_code),
            ("Fill code", self._fill_verification_code)
        ]

        for step_name, step_func in steps:
            try:
                self.ig.account.add_cli(f"Step: {step_name}")
                step_func()
                if step_name != "Wait for code":
                    self.ig.pause(2000, 4000)
            except Exception as e:
                self.ig.account.add_cli(f"Error in step '{step_name}': {str(e)}")
                raise

        self.ig.account.add_cli("Email registration completed!")

    def _click_add_new_contact(self):
        """Click on Add new contact button"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                add_contact_selectors = [
                    'div[aria-label="Add new contact Collapsed"]',
                    'button:has-text("Add new contact")',
                    '[role="button"]:has-text("Add new contact")'
                ]

                for selector in add_contact_selectors:
                    try:
                        self.ig.page.locator(selector).first.click(timeout=10000)
                        self.ig.pause(2000, 3000)
                        if self._is_add_contact_menu_open():
                            return True
                    except:
                        continue

                raise Exception("Could not click on Add new contact")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking add new contact")

        raise Exception("Failed to click on add new contact after 3 attempts.")

    def _is_add_contact_menu_open(self):
        """Check if add contact menu is opened"""
        self.ig.pause(1000, 2000)
        return (self.ig.is_visible_by_text("Add email") or
                self.ig.is_visible_by_text("Add phone number"))

    def _click_add_email(self):
        """Click on Add email"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                add_email_selectors = [
                    'div[role="listitem"]:has-text("Add email")',
                    '[role="button"]:has-text("Add email")',
                    'button:has-text("Add email")'
                ]

                for selector in add_email_selectors:
                    try:
                        email_element = self.ig.page.locator(selector).first
                        if email_element.is_visible():
                            email_element.click(timeout=10000)
                            self.ig.pause(2000, 3000)
                            if self._is_add_email_form_open():
                                return True
                    except:
                        continue

                raise Exception("Could not click on Add email")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking add email")

        raise Exception("Failed to click on add email after 3 attempts.")

    def _is_add_email_form_open(self):
        """Check if add email form is opened"""
        current_url = self.ig.page.url
        url_check = "email" in current_url.lower()

        form_indicators = ["Add an email address", "Email address", "Enter your email"]
        text_check = any(self.ig.is_visible_by_text(indicator) for indicator in form_indicators)

        return url_check and text_check

    def _fill_email_form(self):
        """Fill email in the form"""
        email_input_selectors = [
            'input[placeholder="Enter email address"]',
            'input[id="_r_g_"]',
            'input[type="text"]:visible'
        ]

        for selector in email_input_selectors:
            try:
                email_input = self.ig.page.locator(selector).first
                if email_input.is_visible():
                    email_input.click()
                    self.ig.pause(1500, 2000)
                    email_input.type(self.email, delay=100)
                    return True
            except:
                continue

        raise Exception("Could not find email input field")

    def _check_agreement_checkbox(self):
        """Check the agreement checkbox"""
        checkbox_selectors = [
            'input[type="checkbox"][name="noform"]',
            'input[aria-checked="false"][type="checkbox"]',
            'input[type="checkbox"]'
        ]

        for selector in checkbox_selectors:
            try:
                checkbox = self.ig.page.locator(selector).first
                if checkbox.is_visible():
                    is_checked = checkbox.get_attribute("aria-checked") == "true"
                    if not is_checked:
                        checkbox.click()
                    return True
            except:
                continue

        return True

    def _click_next_button(self):
        """Click the Next button"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                next_button_selectors = [
                    'div[role="button"]:has(span:has-text("Next"))',
                    '[role="button"]:has-text("Next")',
                    'button:has-text("Next")'
                ]

                for selector in next_button_selectors:
                    try:
                        next_button = self.ig.page.locator(selector).first
                        if next_button.is_visible():
                            next_button.click(timeout=10000)
                            self.ig.page.wait_for_load_state("domcontentloaded", timeout=10000)
                            self.ig.pause(3000, 4000)
                            return True
                    except:
                        continue

                raise Exception("Could not click Next button")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking next button")

        raise Exception("Failed to click next button after 3 attempts.")

    def _wait_for_verification_code(self):
        """Wait for verification code with improved logic"""
        try:
            self.ig.account.add_cli("Waiting for verification email...")
            self.page1.bring_to_front()
            self.ig.pause(6000, 8000)

            max_attempts = 20
            for attempt in range(max_attempts):
                if hasattr(self, 'code') and self.code:
                    source = getattr(self, '_code_source', 'UNKNOWN')
                    self.ig.account.add_cli(f"Code ready from: {source} -> {self.code}")
                    break

                try:
                    if self._check_human_verification_temp_mail():
                        raise Exception("Cloudflare Challenge appeared during wait")

                    if self._check_for_new_emails():
                        if hasattr(self, 'code') and self.code:
                            break

                    try:
                        refresh_btn = self.page1.locator('a#click-to-refresh').first
                        if refresh_btn.is_visible(timeout=2000):
                            refresh_btn.click()
                            self.ig.pause(2000, 3000)
                    except:
                        pass

                except Exception as e:
                    self.ig.account.add_cli(f"Error checking for emails (attempt {attempt + 1}): {str(e)}")

                if hasattr(self, 'code') and self.code:
                    break

                if attempt % 3 == 0:
                    self.ig.account.add_cli(f"Still waiting for email... (attempt {attempt + 1}/{max_attempts})")

                self.ig.pause(8000, 10000)

            if not (hasattr(self, 'code') and self.code):
                self._debug_log_code_and_html(source="timeout_no_code_received")
                raise Exception(f"No verification code found after {max_attempts} attempts")

            # LOG: Before switching back to Instagram
            self.ig.account.add_cli("Switching back to Instagram main page...")
            self.ig.page.bring_to_front()
            self.ig.pause(2000, 3000)
            
            # LOG: After switch - check current state
            current_url = self.ig.page.url
            self.ig.account.add_cli(f"DEBUG: Current URL after switch: {current_url}")
            
            try:
                visible_text = self.ig.page.locator('body').inner_text()
                self.ig.account.add_cli(f"DEBUG: Page text preview: {visible_text[:200]}")
            except:
                self.ig.account.add_cli("DEBUG: Could not get page text")

        except Exception as e:
            self.ig.account.add_cli(f"Error waiting for verification code: {str(e)}")
            try:
                self.ig.page.bring_to_front()
            except:
                pass
            raise

    def _check_for_new_emails(self):
        """Check and process new emails intelligently"""
        try:
            email_selectors = [
                'a.viewLink[href*="/view/"]',
                'a[href*="temp-mail.org/en/view/"]'
            ]

            for selector in email_selectors:
                try:
                    elements = self.page1.locator(selector).all()
                    if elements:
                        candidates_info = []
                        for idx, el in enumerate(elements):
                            try:
                                href = el.get_attribute('href') or ''
                            except Exception:
                                href = ''
                            try:
                                text = el.inner_text()[:200] if el.is_visible() else ''
                            except Exception:
                                text = ''
                            candidates_info.append({"idx": idx, "href": href, "text": text})

                        self._debug_log(section="temp_mail_candidates", text=str(candidates_info))

                        scored_emails = []
                        for idx, el in enumerate(elements):
                            score = 0
                            try:
                                text = el.inner_text().lower()
                                href = (el.get_attribute('href') or '').lower()

                                if 'instagram' in text:
                                    score += 100
                                if any(keyword in text for keyword in ['confirmation', 'verify', 'security code', 'confirm email', 'تأیید']):
                                    score += 50
                                if 'no-reply@mail.instagram.com' in text:
                                    score += 30

                                score -= idx * 10

                                scored_emails.append((score, el, idx))

                            except:
                                continue

                        if not scored_emails:
                            return False

                        scored_emails.sort(reverse=True, key=lambda x: x[0])

                        best_score, best_email, best_idx = scored_emails[0]

                        try:
                            chosen_href = best_email.get_attribute('href')
                            chosen_text = ''
                            try:
                                chosen_text = best_email.inner_text()[:200]
                            except Exception:
                                pass
                            self.ig.account.add_cli(f"Clicking email (score: {best_score})")
                            self._debug_log(section="temp_mail_clicked",
                                            text=f"href={chosen_href}\ntext={chosen_text}\nscore={best_score}")
                        except Exception:
                            pass

                        best_email.click()
                        self.page1.wait_for_load_state("domcontentloaded", timeout=10000)

                        if self._wait_for_email_content_to_load():
                            self._extract_code_from_opened_email()

                            if hasattr(self, 'code') and self.code:
                                return True

                        return False

                except Exception as e:
                    continue

            return False

        except Exception as e:
            self.ig.account.add_cli(f"Error in _check_for_new_emails: {str(e)}")
            return False

    def _wait_for_email_content_to_load(self):
        """Wait for email content to be fully loaded"""
        try:
            self.ig.account.add_cli("Waiting for email content to load...")

            max_wait_attempts = 12
            for attempt in range(max_wait_attempts):
                try:
                    current_url = self.page1.url
                    
                    if '/view/' not in current_url:
                        self.ig.account.add_cli("WARNING: Not in email view page!")
                        self.ig.pause(1500, 2000)
                        continue
                    
                    visible_text = self.page1.locator('body').inner_text()
                    
                    has_content = (
                        len(visible_text) > 200 and
                        ('Instagram' in visible_text or 'instagram' in visible_text or 'تأیید' in visible_text)
                    )
                    
                    if has_content:
                        self.ig.account.add_cli(f"Email content loaded ({len(visible_text)} chars)")
                        self.ig.pause(2000, 3000)
                        return True
                    
                    if attempt % 3 == 0:
                        self.ig.account.add_cli(f"Loading... ({attempt + 1}/{max_wait_attempts}) - {len(visible_text)} chars")

                except Exception as e:
                    self.ig.account.add_cli(f"Error in wait attempt {attempt + 1}: {str(e)}")

                self.ig.pause(1500, 2000)

            self.ig.account.add_cli("WARNING: Proceeding despite content not fully loaded")
            self.ig.pause(3000, 4000)
            return True

        except Exception as e:
            self.ig.account.add_cli(f"Error waiting for email content: {str(e)}")
            return True

    def _extract_code_from_opened_email(self):
        """Extract verification code with improved prioritized methods"""
        try:
            if hasattr(self, 'code'):
                delattr(self, 'code')

            self.ig.pause(3000, 4000)

            try:
                visible_text = self.page1.locator('body').inner_text()
            except:
                visible_text = ""

            if visible_text and self._extract_from_visible_text_with_context(visible_text):
                return

            if self._extract_from_html_with_style_priority():
                return

            page_content = self.page1.content()
            self._extract_from_page_content_filtered(page_content, visible_text)

            if not hasattr(self, 'code') or not self.code:
                self.ig.account.add_cli("WARNING: No code extracted from any method!")
                self._debug_log_code_and_html(source="extraction_failed_all_methods")

        except Exception as e:
            self.ig.account.add_cli(f"Error extracting code: {str(e)}")

    def _extract_from_visible_text_with_context(self, visible_text: str) -> bool:
        """Extract code from visible text with strong context checking"""

        instagram_context_patterns = [
            r'(?:confirmation|تأیید).*?(?:code|کد)[:\s]*[‏\u200f]*(\d{6})[‏\u200f]*',
            r'(?:enter|وارد کنید).*?(?:code|کد)[:\s]*[‏\u200f]*(\d{6})[‏\u200f]*',
            r'Instagram.*?[:\s]*[‏\u200f]*(\d{6})[‏\u200f]*',
            r'(?:verify|security)[:\s]*code[:\s]*(\d{6})',
        ]

        for idx, pattern in enumerate(instagram_context_patterns):
            match = re.search(pattern, visible_text, re.IGNORECASE | re.DOTALL)
            if match:
                candidate_code = match.group(1)
                if self._is_likely_verification_code(candidate_code, visible_text):
                    self.code = candidate_code
                    self._code_source = f"SCRAPE_VISIBLE_TEXT_PATTERN_{idx}"
                    self.ig.account.add_cli(f"[SCRAPE-PATTERN-{idx}] Found code: {self.code}")
                    self._debug_log_code_and_html(source=f"visible_text_context_pattern_{idx}")
                    return True

        lines = visible_text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()

            if re.match(r'^\s*[‏\u200f]*(\d{6})[‏\u200f]*\s*$', line_clean):
                match = re.search(r'(\d{6})', line_clean)
                if match:
                    candidate_code = match.group(1)

                    if not self._is_likely_verification_code(candidate_code, line_clean):
                        continue

                    context_window = '\n'.join(lines[max(0, i-3):min(len(lines), i+4)])

                    good_keywords = ['instagram', 'confirmation', 'verify', 'تأیید', 'کد', 'security code', 'confirm email']
                    bad_keywords = ['javascript', 'var ', 'function', 'padding', 'color:', 'style', 'script', 'paddle']

                    has_good_context = any(keyword in context_window.lower() for keyword in good_keywords)
                    has_bad_context = any(keyword in context_window.lower() for keyword in bad_keywords)

                    if has_good_context and not has_bad_context:
                        self.code = candidate_code
                        self._code_source = "SCRAPE_VISIBLE_TEXT_STANDALONE"
                        self.ig.account.add_cli(f"[SCRAPE-STANDALONE] Found code: {self.code}")
                        self._debug_log_code_and_html(source="visible_text_standalone_with_good_context")
                        return True

        return False

    def _extract_from_html_with_style_priority(self) -> bool:
        """Extract code from HTML elements with style attributes (Instagram's format)"""
        try:
            style_selectors = [
                'td[style*="font-size: 32px"]',
                'td[style*="font-size: 30px"]',
                'td[style*="text-align: center"][style*="font-size"]',
                'p[style*="font-size: 32px"]',
            ]

            for idx, selector in enumerate(style_selectors):
                try:
                    elements = self.page1.locator(selector).all()
                    for element in elements:
                        try:
                            element_text = element.inner_text().strip()
                            element_text_clean = element_text.replace('‏', '').replace('\u200f', '').strip()

                            if len(element_text_clean) == 6 and element_text_clean.isdigit():
                                element_html = element.inner_html()
                                if self._is_likely_verification_code(element_text_clean, element_html):
                                    self.code = element_text_clean
                                    self._code_source = f"SCRAPE_HTML_STYLE_{idx}"
                                    self.ig.account.add_cli(f"[SCRAPE-HTML-STYLE-{idx}] Found code: {self.code}")
                                    self._debug_log_code_and_html(source=f"html_style_selector_{selector}")
                                    return True
                        except:
                            continue
                except:
                    continue

            return False

        except Exception as e:
            return False

    def _extract_from_page_content_filtered(self, page_content: str, visible_text: str):
        """Extract from page content with heavy filtering"""
        try:
            html_text_patterns = [
                r'<td[^>]*style="[^"]*font-size:\s*32px[^"]*"[^>]*>[\s‏\u200f]*(\d{6})[\s‏\u200f]*</td>',
                r'<p[^>]*>[\s‏\u200f]*(\d{6})[\s‏\u200f]*</p>',
            ]

            for idx, pattern in enumerate(html_text_patterns):
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                for match in matches:
                    candidate_code = match.strip()
                    if len(candidate_code) == 6 and candidate_code.isdigit():
                        if self._is_likely_verification_code(candidate_code, page_content):
                            self.code = candidate_code
                            self._code_source = f"SCRAPE_HTML_PATTERN_{idx}"
                            self.ig.account.add_cli(f"[SCRAPE-HTML-PATTERN-{idx}] Found code: {self.code}")
                            self._debug_log_code_and_html(source="html_text_pattern_filtered")
                            return

            safe_tag_patterns = [
                r'<td[^>]*>(\d{6})</td>',
                r'<p[^>]*>(\d{6})</p>',
                r'<span[^>]*>(\d{6})</span>',
            ]

            all_found_codes = []
            for pattern in safe_tag_patterns:
                matches = re.findall(pattern, page_content)
                for match in matches:
                    code_candidate = match[0] if isinstance(match, tuple) else match
                    if len(code_candidate) == 6 and code_candidate.isdigit():
                        all_found_codes.append(code_candidate)

            if all_found_codes:
                for candidate_code in all_found_codes:
                    if self._is_likely_verification_code(candidate_code, visible_text):
                        self.code = candidate_code
                        self._code_source = "SCRAPE_HTML_SAFE_TAGS"
                        self.ig.account.add_cli(f"[SCRAPE-SAFE-TAGS] Found code: {self.code}")
                        self._debug_log_code_and_html(source="html_safe_tags_pattern")
                        return

        except Exception as e:
            self.ig.account.add_cli(f"Error in content extraction: {str(e)}")

    def _is_likely_verification_code(self, code: str, context: str = "") -> bool:
        """Enhanced validation using context analysis"""
        if len(code) != 6 or not code.isdigit():
            return False

        sequential_patterns = [
            r'012345', r'123456', r'234567', r'345678', r'456789',
            r'543210', r'654321', r'765432', r'876543', r'987654',
            r'000000', r'111111', r'222222', r'333333', r'444444',
            r'555555', r'666666', r'777777', r'888888', r'999999'
        ]

        if any(re.match(pattern, code) for pattern in sequential_patterns):
            return False

        if code.startswith(('2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030')):
            return False

        context_lower = context.lower() if context else ""

        bad_context_keywords = [
            'paddlemonth',
            'paddleyear',
            'var ',
            'javascript',
            'color:#',
            'color: #',
            'rgb(',
            'rgba(',
            'font-family:',
            '.css',
            'px;',
            'stylesheet',
            'api_url',
            'papi_url',
            'url_domain',
            'geodetectionservice',
            'adlayer',
            '<style',
            '<script',
            'function(',
            'window.',
            'document.'
        ]

        code_position_in_context = context_lower.find(code.lower())
        if code_position_in_context != -1:
            surrounding_text = context_lower[max(0, code_position_in_context - 200):
                                             min(len(context_lower), code_position_in_context + 206)]

            for bad_keyword in bad_context_keywords:
                if bad_keyword.lower() in surrounding_text:
                    rejection_reason = f"found '{bad_keyword}'"
                    self.ig.account.add_cli(f"REJECTED {code}: {rejection_reason}")
                    self._debug_log(section="code_rejected", 
                                   text=f"CODE: {code}\nREASON: {rejection_reason}\nCONTEXT: {surrounding_text[:300]}")
                    return False

        good_context_keywords = [
            'instagram',
            'confirmation',
            'verify',
            'security code',
            'enter this code',
            'تأیید',
            'کد تأیید',
            'no-reply@mail.instagram.com',
            'confirm email',
            'confirmation code'
        ]

        if context:
            has_good_context = any(keyword in context_lower for keyword in good_context_keywords)
            
            if len(context) > 100:
                if not has_good_context:
                    self.ig.account.add_cli(f"REJECTED {code}: no good keywords in context")
                    return False
            
            if has_good_context:
                self.ig.account.add_cli(f"ACCEPTED {code}: good context found")
                return True

            if code_position_in_context != -1:
                self.ig.account.add_cli(f"REJECTED {code}: in context but no good keywords")
                return False

        return False

    def _fill_verification_code(self):
        """Fill verification code with enhanced debugging"""
        max_retries = 3

        # LOG: Initial state check
        self.ig.account.add_cli("=" * 50)
        self.ig.account.add_cli("DEBUG: Starting _fill_verification_code")
        
        current_url = self.ig.page.url
        self.ig.account.add_cli(f"DEBUG: Current URL: {current_url}")
        
        try:
            page_title = self.ig.page.title()
            self.ig.account.add_cli(f"DEBUG: Page title: {page_title}")
        except:
            self.ig.account.add_cli("DEBUG: Could not get page title")
        
        # LOG: Check what's visible on page
        try:
            visible_text = self.ig.page.locator('body').inner_text()
            self.ig.account.add_cli(f"DEBUG: Page visible text (first 300 chars): {visible_text[:300]}")
        except Exception as e:
            self.ig.account.add_cli(f"DEBUG: Could not get visible text: {str(e)}")
        
        # LOG: Check for verification code input existence
        self.ig.account.add_cli("DEBUG: Checking for verification code inputs...")
        
        all_inputs = self.ig.page.locator('input').all()
        self.ig.account.add_cli(f"DEBUG: Found {len(all_inputs)} total inputs on page")
        
        for idx, inp in enumerate(all_inputs):
            try:
                input_info = {
                    'index': idx,
                    'id': inp.get_attribute('id') or 'none',
                    'name': inp.get_attribute('name') or 'none',
                    'type': inp.get_attribute('type') or 'none',
                    'placeholder': inp.get_attribute('placeholder') or 'none',
                    'maxlength': inp.get_attribute('maxlength') or 'none',
                    'autocomplete': inp.get_attribute('autocomplete') or 'none',
                    'inputmode': inp.get_attribute('inputmode') or 'none',
                    'visible': inp.is_visible(),
                    'enabled': not inp.is_disabled()
                }
                self.ig.account.add_cli(f"DEBUG: Input[{idx}]: {input_info}")
            except Exception as e:
                self.ig.account.add_cli(f"DEBUG: Error getting input[{idx}] info: {str(e)}")
        
        # LOG: Screenshot before fill attempt
        try:
            screenshot_path = f'debug_fill_code_{self.ig.account.username}_{datetime.now().strftime("%H%M%S")}.png'
            self.ig.page.screenshot(path=screenshot_path)
            self.ig.account.add_cli(f"DEBUG: Screenshot saved: {screenshot_path}")
        except:
            pass
        
        self.ig.account.add_cli("=" * 50)

        for attempt in range(max_retries):
            try:
                if not hasattr(self, 'code') or not self.code:
                    raise Exception("No verification code available")

                source = getattr(self, '_code_source', 'UNKNOWN')
                self.ig.account.add_cli(f"Filling code: {self.code} from [{source}] (Attempt {attempt + 1})")

                if attempt == 0:
                    self._debug_log_code_and_html(source="before_fill_code")

                code_input_selectors = [
                    'input[autocomplete="one-time-code"]',
                    'input[inputmode="numeric"][maxlength="6"]',
                    'input[type="text"][maxlength="6"]',
                    'input[id^="_r_"]',
                    'input[placeholder*="confirmation code"]',
                ]

                self.ig.account.add_cli(f"DEBUG: Trying {len(code_input_selectors)} selectors...")

                input_found = False
                for selector_idx, selector in enumerate(code_input_selectors):
                    try:
                        self.ig.account.add_cli(f"DEBUG: Trying selector[{selector_idx}]: {selector}")
                        
                        code_input = self.ig.page.locator(selector).first
                        
                        # Check if exists
                        count = self.ig.page.locator(selector).count()
                        self.ig.account.add_cli(f"DEBUG: Selector matched {count} elements")
                        
                        if count == 0:
                            self.ig.account.add_cli(f"DEBUG: Selector[{selector_idx}] - No elements found")
                            continue
                        
                        # Check visibility with longer timeout
                        is_visible = code_input.is_visible()
                        self.ig.account.add_cli(f"DEBUG: Selector[{selector_idx}] - is_visible: {is_visible}")
                        
                        if is_visible:
                            self.ig.account.add_cli(f"DEBUG: Selector[{selector_idx}] - Element is visible, attempting click...")
                            
                            code_input.click(timeout=5000)
                            self.ig.pause(500, 800)

                            try:
                                code_input.fill("")
                                self.ig.pause(300, 500)
                            except:
                                pass

                            self.ig.account.add_cli(f"DEBUG: Typing code: {self.code}")
                            code_input.type(self.code, delay=random.randint(80, 150))
                            self.ig.pause(1000, 1500)

                            input_value = code_input.input_value()
                            self.ig.account.add_cli(f"DEBUG: Input value after typing: {input_value}")
                            
                            if input_value == self.code:
                                self.ig.account.add_cli(f"SUCCESS: Code verified in input: {input_value}")
                                input_found = True
                                break
                            else:
                                self.ig.account.add_cli(f"WARNING: Code mismatch - expected {self.code}, got {input_value}")
                        else:
                            self.ig.account.add_cli(f"DEBUG: Selector[{selector_idx}] - Element not visible")

                    except Exception as e:
                        self.ig.account.add_cli(f"DEBUG: Selector[{selector_idx}] failed: {str(e)}")
                        continue

                if not input_found:
                    self.ig.account.add_cli("ERROR: All selectors failed - waiting 5s and taking screenshot...")
                    self.ig.pause(5000, 5000)
                    
                    try:
                        screenshot_path = f'debug_fill_failed_{self.ig.account.username}_{datetime.now().strftime("%H%M%S")}.png'
                        self.ig.page.screenshot(path=screenshot_path)
                        self.ig.account.add_cli(f"DEBUG: Failure screenshot saved: {screenshot_path}")
                    except:
                        pass
                    
                    raise Exception("Could not find or fill verification code input field")

                self._click_submit_code_button()

                if self._check_for_wrong_code_error():
                    self.ig.account.add_cli(f"ERROR: Wrong code for: {self.code}")
                    if attempt < max_retries - 1:
                        self.ig.pause(2000, 3000)
                        continue
                    else:
                        raise Exception(f"Verification code {self.code} was rejected as wrong")

                return True

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise

        raise Exception("Failed to fill verification code after all attempts")

    def _click_submit_code_button(self):
        """Click Next button after filling verification code"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                submit_button_selectors = [
                    'div[role="button"][tabindex="0"]:has(span:has-text("Next"))',
                    '[role="button"]:has-text("Next")',
                    'button:has-text("Next")'
                ]

                for selector in submit_button_selectors:
                    try:
                        submit_buttons = self.ig.page.locator(selector).all()
                        if submit_buttons:
                            for button in submit_buttons:
                                if button.is_visible():
                                    button.click(timeout=10000, force=True)
                                    self.ig.page.wait_for_load_state("domcontentloaded", timeout=15000)
                                    self.ig.pause(2000, 3000)

                                    if self._check_for_wrong_code_error():
                                        self.ig.account.add_cli("ERROR: Wrong verification code detected!")
                                        return False

                                    if self._is_email_added_successfully():
                                        self.ig.account.add_cli("SUCCESS: Email successfully added!")
                                        self.ig.pause(4000, 4000)
                                        return True

                                    return True
                    except:
                        continue

                raise Exception("Could not click submit button")

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for clicking submit code button")

        raise Exception("Failed to click submit code button after 3 attempts.")

    def _get_debug_log_path(self):
        """Build per-account debug log file path for this run."""
        if self._debug_log_path:
            return self._debug_log_path
        username = getattr(self.ig.account, 'username', 'unknown') or 'unknown'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir = os.path.join('logs', 'register_email', username)
        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception:
            base_dir = '.'
        self._debug_log_path = os.path.join(base_dir, f'temp_mail_debug_{timestamp}.log')
        return self._debug_log_path

    def _debug_log_code_and_html(self, source="unknown"):
        """Append extracted code and full temp-mail HTML into a per-account log file."""
        try:
            log_path = self._get_debug_log_path()
            code_value = getattr(self, 'code', None)
            code_source = getattr(self, '_code_source', 'UNKNOWN')
            
            html_content = ''
            try:
                if hasattr(self, 'page1') and self.page1:
                    try:
                        visible_text = self.page1.locator('body').inner_text()
                    except Exception:
                        visible_text = ''
                    page_html = self.page1.content()
                    html_content = f"\n===== VISIBLE TEXT =====\n{visible_text}\n\n===== FULL HTML =====\n{page_html}"
            except Exception:
                pass

            with open(log_path, 'a', encoding='utf-8', errors='ignore') as f:
                f.write(f"\n===== {datetime.now().isoformat()} SOURCE:{source} =====\n")
                f.write(f"CODE: {code_value}\n")
                f.write(f"CODE_SOURCE: {code_source}\n")
                if html_content:
                    f.write(html_content)
                    f.write("\n")
        except Exception:
            pass

    def _debug_log(self, section: str, text: str):
        """Append arbitrary debug text to the per-account log file."""
        try:
            log_path = self._get_debug_log_path()
            with open(log_path, 'a', encoding='utf-8', errors='ignore') as f:
                f.write(f"\n===== {datetime.now().isoformat()} {section} =====\n")
                f.write(text)
                f.write("\n")
        except Exception:
            pass

    def _check_for_wrong_code_error(self):
        """Check if wrong verification code error is displayed"""
        error_messages = [
            "Wrong code: That code didn't work. Please check the code and try again.",
            "That code didn't work",
            "Wrong code"
        ]
        return any(self.ig.is_visible_by_text(error) for error in error_messages)

    def _is_email_added_successfully(self):
        """Check if email was added successfully"""
        success_messages = [
            "You've added your email",
            "Email added successfully",
            "Email verified",
            "Contact information updated"
        ]

        for msg in success_messages:
            if self.ig.is_visible_by_text(msg):
                self.ig.account.add_cli(f"Success message found: {msg}")
                self._mark_account_verified()
                return True

        current_url = self.ig.page.url
        if "contact_points" in current_url or "contact_info" in current_url:
            if "email" not in current_url.lower() or "add" not in current_url.lower():
                self.ig.account.add_cli("URL indicates success (back to contact info)")
                self._mark_account_verified()
                return True

        self.ig.pause(2000, 3000)
        if self._has_verified_email():
            self.ig.account.add_cli("Verified email icon found")
            self._mark_account_verified()
            return True

        return False

    def _mark_account_verified(self):
        """Mark account as verified"""
        if not self.ig.account.is_verify:
            self.ig.account.is_verify = 1
            self.ig.account.save()
            self.ig.account.add_cli("Account marked as verified")

    def _has_verified_email(self):
        """Check if verified email exists"""
        email_selectors = [
            'div[role="listitem"]:has(svg path[d*="18.629 4c1.431"]):not(:has-text("Pending"))',
            'button:has(svg path[d*="18.629 4c1.431"]):not(:has-text("Pending"))'
        ]
        return any(self.ig.page.locator(selector).is_visible() for selector in email_selectors)

    def _has_verified_phone(self):
        """Check if verified phone exists"""
        phone_selectors = [
            'div[role="listitem"]:has(svg path[d*="15.66 14.026"]):not(:has-text("Pending"))',
            'button:has(svg path[d*="15.66 14.026"]):not(:has-text("Pending"))'
        ]
        return any(self.ig.page.locator(selector).is_visible() for selector in phone_selectors)

    def _has_only_pending_phone(self):
        """Check if only pending phone exists"""
        pending_phone_exists = self.ig.is_visible_by_text("Pending confirmation")
        email_exists = self.ig.page.locator('svg path[d*="18.629 4c1.431"]').is_visible()
        verified_phone_exists = self._has_verified_phone()
        return pending_phone_exists and not email_exists and not verified_phone_exists

    def close_temp_mail_tab_manually(self):
        """Manual method to close temp mail tab"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                if hasattr(self, 'page1') and self.page1:
                    self.page1.close()
                    self.ig.account.add_cli("Temp mail tab closed manually")
                    return True
                return False

            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed for closing temp mail tab: {str(e)}")

        raise Exception("Failed to close temp mail tab after 3 attempts.")