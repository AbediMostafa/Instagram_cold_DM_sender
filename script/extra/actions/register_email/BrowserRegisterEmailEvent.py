from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.helper import go_to_page
import time
import random
import re


class BrowserRegisterEmailEvent(InstagramMiddleware):
    """
    Event class for executing email registration on Instagram
    """

    def init(self):
        """
        Initialize and execute the email registration process
        """
        try:
            self.ig.account.add_cli("Starting email registration process...")
            self._navigate_to_contact_info()
            self._analyze_contact_info()

        except Exception as e:
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
                self.ig.pause(4000, 6000)

                if not verify_func():
                    self.ig.account.add_cli(f"Failed to reach {step_name}")
                    raise Exception(f"Failed to reach {step_name}")
            except Exception as e:
                self.ig.account.add_cli(f"Error in {step_name}: {str(e)}")
                raise

    def _click_on_profile(self):
        """Click on profile using different methods"""
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

    def _is_in_profile_page(self):
        """Check if we are in profile page"""
        current_url = self.ig.page.url
        url_check = f"/{self.ig.account.username}/" in current_url
        text_check = (self.ig.is_visible_by_text("posts") or
                     self.ig.is_visible_by_text("followers") or
                     self.ig.is_visible_by_text("following"))
        return url_check and text_check

    def _click_on_options(self):
        """Click on Options button"""
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

    def _is_options_menu_open(self):
        """Check if options menu is opened"""
        menu_indicators = ["Settings and privacy", "Your activity", "Archive", "QR code"]
        return any(self.ig.is_visible_by_text(indicator) for indicator in menu_indicators)

    def _click_on_settings_and_privacy(self):
        """Click on Settings and privacy button"""
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

    def _is_settings_page_open(self):
        """Check if settings page is opened"""
        current_url = self.ig.page.url
        url_check = "accounts/edit" in current_url
        text_check = (self.ig.is_visible_by_text("Settings") or
                     self.ig.is_visible_by_text("Edit profile"))
        return url_check and text_check

    def _click_on_accounts_center(self):
        """Click on Accounts Center"""
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

        # Check if already in accounts center
        current_url = self.ig.page.url
        if "accountscenter.instagram.com" in current_url:
            if self._is_accounts_center_page_open():
                return True

        raise Exception("Could not click on Accounts Center")

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

    def _is_personal_details_page_open(self):
        """Check if personal details page is opened"""
        current_url = self.ig.page.url
        url_check = "accountscenter.instagram.com/personal_info/" in current_url
        text_check = self.ig.is_visible_by_text("Personal details")
        return url_check and text_check

    def _click_on_contact_info(self):
        """Click on Contact info"""
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
                raise Exception('Human verification detected on temp mail')

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

                # Extract code from subject first
                match = re.search(r'\b\d{6}\b', subject)
                if match:
                    self.code = match.group()
                    self.ig.account.add_cli(f"Found verification code: {self.code}")
                    return

                # Try Instagram patterns in body
                instagram_patterns = [
                    r'Instagram.*?(\d{6})',
                    r'confirmation.*?code.*?(\d{6})',
                    r'verify.*?(\d{6})'
                ]

                for pattern in instagram_patterns:
                    match = re.search(pattern, body, re.IGNORECASE)
                    if match:
                        self.code = match.group(1)
                        self.ig.account.add_cli(f"Found verification code: {self.code}")
                        return

                # Last resort - standalone codes
                standalone_pattern = r'(?<![a-zA-Z0-9/])(\d{6})(?![a-zA-Z0-9/])'
                matches = re.findall(standalone_pattern, body)

                for code in matches:
                    if code not in ['000000', '123456', '999999'] and not code.startswith('20'):
                        self.code = code
                        self.ig.account.add_cli(f"Found verification code: {self.code}")
                        return

        except Exception as e:
            self.ig.account.add_cli(f"Error processing temp mail response: {str(e)}")

    def _check_human_verification_temp_mail(self):
        """Check if human verification is required in temp mail tab"""
        verification_indicators = [
            'Verify you are human',
            'temp-mail.org needs to review the security'
        ]
        return any(self.page1.locator(f'text="{indicator}"').is_visible()
                  for indicator in verification_indicators)

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

    def _is_add_contact_menu_open(self):
        """Check if add contact menu is opened"""
        self.ig.pause(1000, 2000)
        return (self.ig.is_visible_by_text("Add email") or
               self.ig.is_visible_by_text("Add phone number"))

    def _click_add_email(self):
        """Click on Add email"""
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

    def _wait_for_verification_code(self):
        """Wait for verification code"""
        try:
            self.ig.account.add_cli("Waiting for verification email...")
            self.page1.bring_to_front()
            self.ig.pause(3000, 5000)

            max_attempts = 15
            for attempt in range(max_attempts):
                if hasattr(self, 'code') and self.code:
                    self.ig.account.add_cli(f"Using verification code: {self.code}")
                    break

                email_selectors = [
                    'a.viewLink[href*="/view/"]',
                    'a[href*="temp-mail.org/en/view/"]'
                ]

                for selector in email_selectors:
                    try:
                        elements = self.page1.locator(selector).all()
                        if elements:
                            first_email = elements[0]
                            email_href = first_email.get_attribute('href')

                            if email_href and 'temp-mail.org/en/view/' in email_href:
                                first_email.click()
                                self.page1.wait_for_load_state("domcontentloaded", timeout=10000)
                                self.ig.pause(3000, 5000)
                                self._extract_code_from_opened_email()

                                if hasattr(self, 'code') and self.code:
                                    self.ig.account.add_cli(f"Extracted verification code: {self.code}")
                                    break
                            break
                    except:
                        continue

                if hasattr(self, 'code') and self.code:
                    break

                self.ig.pause(8000, 12000)

            if not (hasattr(self, 'code') and self.code):
                raise Exception("No verification code found after waiting")

            self.ig.page.bring_to_front()
            self.ig.pause(2000, 3000)

        except Exception as e:
            self.ig.account.add_cli(f"Error waiting for verification code: {str(e)}")
            try:
                self.ig.page.bring_to_front()
            except:
                pass
            raise

    def _extract_code_from_opened_email(self):
        """Extract verification code with prioritized methods"""
        try:
            if hasattr(self, 'code'):
                delattr(self, 'code')

            self.ig.pause(4000, 6000)

            page_content = self.page1.content()
            try:
                visible_text = self.page1.locator('body').inner_text()
            except:
                visible_text = ""

            # Priority 1: Standalone 6-digit codes in visible text
            if visible_text:
                lines = visible_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'^\s*(\d{6})\s*$', line):
                        code_match = re.search(r'(\d{6})', line)
                        if code_match:
                            self.code = code_match.group(1)
                            return

            # Priority 2: Instagram HTML patterns
            instagram_html_selectors = [
                '*[style*="font-size: 32px"]',
                '*[style*="font-size: 30px"]',
                '*[style*="text-align: center"][style*="font-size"]'
            ]

            for selector in instagram_html_selectors:
                try:
                    elements = self.page1.locator(selector).all()
                    for element in elements:
                        try:
                            element_text = element.inner_text().strip()
                            if len(element_text) == 6 and element_text.isdigit():
                                self.code = element_text
                                return
                        except:
                            continue
                except:
                    continue

            # Priority 3: Text patterns
            instagram_text_patterns = [
                r'confirmation\s*code[:\s]*(\d{6})',
                r'enter\s*this[^:]*code[:\s]*(\d{6})',
                r'verify[^:]*code[:\s]*(\d{6})'
            ]

            for pattern in instagram_text_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    code_candidate = match.strip()
                    if len(code_candidate) == 6 and code_candidate.isdigit():
                        self.code = code_candidate
                        return

            # Priority 4: General patterns with filtering
            general_patterns = [r'>(\d{6})<', r'\b(\d{6})\b']

            found_codes = []
            for pattern in general_patterns:
                matches = re.findall(pattern, page_content)
                for match in matches:
                    code_candidate = match[0] if isinstance(match, tuple) else match
                    if len(code_candidate) == 6 and code_candidate.isdigit():
                        found_codes.append(code_candidate)

            if found_codes:
                unique_codes = list(dict.fromkeys(found_codes))
                self.code = unique_codes[0]

        except Exception as e:
            self.ig.account.add_cli(f"Error extracting code: {str(e)}")

    def _fill_verification_code(self):
        """Fill verification code"""
        if not hasattr(self, 'code') or not self.code:
            raise Exception("No verification code available")

        self.ig.account.add_cli(f"Filling verification code: {self.code}")

        code_input_selectors = [
            'input[id="_r_o_"]',
            'input[placeholder="Enter confirmation code"]',
            'input[autocomplete="one-time-code"]',
            'input[inputmode="numeric"][maxlength="6"]'
        ]

        for selector in code_input_selectors:
            try:
                code_input = self.ig.page.locator(selector).first
                if code_input.is_visible():
                    code_input.click()
                    self.ig.pause(1000, 1500)
                    code_input.fill("")
                    code_input.type(self.code, delay=100)
                    self.ig.pause(1000, 2000)
                    self._click_submit_code_button()
                    return True
            except:
                continue

        raise Exception("Could not find verification code input field")

    def _click_submit_code_button(self):
        """Click Next button after filling verification code"""
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
                                self.ig.account.add_cli("Wrong verification code detected!")
                                return False

                            if self._is_email_added_successfully():
                                self.ig.account.add_cli("Email successfully added!")
                                self.ig.pause(4000, 4000)  # Wait 4 seconds after success
                                return True

                            return True
            except:
                continue

        return False

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
        if self.ig.is_visible_by_text("You've added your email to the accounts selected"):
            self.ig.account.is_verify = 1
            self.ig.account.save()
            return True

        current_url = self.ig.page.url
        if "contact_points" in current_url or "contact_info" in current_url:
            self.ig.account.is_verify = 1
            self.ig.account.save()
            return True

        success_indicators = [
            "Email added successfully",
            "Email verified",
            "Contact information updated"
        ]

        success = any(self.ig.is_visible_by_text(indicator) for indicator in success_indicators)
        if success:
            self.ig.account.is_verify = 1
            self.ig.account.save()

        return success

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
        try:
            if hasattr(self, 'page1') and self.page1:
                self.page1.close()
                self.ig.account.add_cli("Temp mail tab closed manually")
        except Exception as e:
            self.ig.account.add_cli(f"Error closing temp mail tab: {str(e)}")