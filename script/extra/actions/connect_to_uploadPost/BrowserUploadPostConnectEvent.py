import os
import requests
from dotenv import load_dotenv
from peewee import fn

load_dotenv()

# Upload-Post API base URL and key loaded from environment variables.
# UPLOAD_POST_API_KEY must be set in the .env file.
UPLOAD_POST_BASE_URL = 'https://api.upload-post.com/api'
UPLOAD_POST_API_KEY = os.getenv('UPLOAD_POST_API_KEY', '')


class BrowserUploadPostConnectEvent:
    """
    Module responsible for connecting/disconnecting Instagram accounts to Upload-Post.

    Lifecycle:
      1. Check upload_post_status on the account
      2. If 'pending'       -> run the connect flow
      3. If 'disconnecting' -> run the disconnect flow
      4. Otherwise          -> skip (not actionable)

    Connect flow:
      - Assign a sequential numeric profile name (001, 002, ...) if not already assigned
      - Create a profile on Upload-Post with that number
      - Generate a JWT-based access URL (valid for 48h)
      - Open the URL in the current AdsPower browser
      - Complete the OAuth flow (Facebook/Instagram permission grant)
      - Verify connection via the Upload-Post API
      - Update upload_post_status to 'connected' or revert to original status on failure

    Disconnect flow:
      - Call the Upload-Post delete profile API using upload_post_username
      - Reset upload_post_status to 'none' (upload_post_username is kept, never reused)
    """

    def __init__(self, ig):
        self.ig = ig
        self.account = ig.account
        self.headers = {
            'Authorization': f'ApiKey {UPLOAD_POST_API_KEY}',
            'Content-Type': 'application/json',
        }

    def init(self):
        """
        Entry point called by Context via BrowserUploadPostConnectEvent(ig).init().
        First cleans up one suspended account's Upload-Post profile, then
        checks the current account's upload_post_status and routes to connect or disconnect.
        """
        # clean up one suspended account's Upload-Post profile per cycle
        self._cleanup_one_suspended_profile()

        status = self.account.upload_post_status

        if status == 'pending':
            self.account.add_cli('[UploadPost] Status is pending, starting connect flow...')
            self._connect()

        elif status == 'disconnecting':
            self.account.add_cli('[UploadPost] Status is disconnecting, starting disconnect flow...')
            self._disconnect()

        else:
            self.account.add_cli(f'[UploadPost] Status is "{status}", skipping...')

    # -------------------------------------------------------------------------
    # Connect flow
    # -------------------------------------------------------------------------

    def _connect(self):
        """
        Full connect flow: assign number -> create profile -> generate JWT -> open browser -> OAuth -> verify.
        On failure, status reverts to the original value (e.g. 'pending') so the worker
        can retry automatically in the next cycle.
        """
        # Remember original status so we can revert on failure instead of marking as 'failed'
        original_status = self.account.upload_post_status

        try:
            # Mark as connecting so other workers won't pick this account
            self._update_status('connecting')

            # Step 0: Assign a sequential profile number if not already assigned.
            # This is atomic to prevent duplicate numbers across concurrent threads.
            profile_username = self._get_or_assign_profile_username()

            # Step 1: Create a profile on Upload-Post using the assigned number
            self._create_profile(profile_username)

            # Step 2: Generate the secure access URL (JWT link, valid 48h)
            access_url = self._generate_jwt(profile_username)

            # Step 3: Open the access URL in the current AdsPower browser
            self._open_access_url(access_url)

            # Step 4: Complete OAuth flow
            self._already_connected = False
            self._complete_oauth()

            # If Instagram was already connected on the Upload-Post page, skip verify
            if self._already_connected:
                self._update_status('connected')
                self.account.add_cli('[UploadPost] Already connected - status updated to connected')
            else:
                # Step 5: Wait for Upload-Post to fully register the connection before verifying.
                # Upload-Post may take a few seconds to process the OAuth callback.
                self.account.add_cli('[UploadPost] Waiting for Upload-Post to register connection...')
                self.ig.pause(10000, 15000)

                # Step 6: Verify that Instagram is actually connected
                is_connected = self._verify_connection(profile_username)

                if is_connected:
                    self._update_status('connected')
                    self.account.add_cli('[UploadPost] Successfully connected!')
                else:
                    # Revert to original status so worker can retry in the next cycle
                    self._update_status(original_status)
                    self.account.add_cli(f'[UploadPost] Verification failed - reverted to "{original_status}" for retry')

        except Exception as e:
            # Revert to original status so worker can retry in the next cycle
            self._update_status(original_status)
            self.account.add_cli(f'[UploadPost] Connect failed: {str(e)} - reverted to "{original_status}" for retry')

        finally:
            # Always navigate back to Instagram home page regardless of success or failure.
            # This ensures the browser is in a clean state for the next module.
            self.account.add_cli('[UploadPost] Navigating back to Instagram home...')
            try:
                self.ig.page.goto('https://www.instagram.com/', timeout=60000)
                self.ig.pause(6000, 10000)
            except Exception:
                self.account.add_cli('[UploadPost] Failed to navigate back to Instagram home')

    def _get_or_assign_profile_username(self):
        """
        Step 0: Get existing or assign a new sequential profile number.

        If the account already has an upload_post_username (e.g. from a failed retry),
        reuse it. Otherwise, atomically get the next number by finding the current max
        and incrementing it.

        Uses database.atomic() to prevent race conditions when multiple threads
        are assigning numbers simultaneously.

        Format: '001', '002', ..., '999', '1000', etc. (zero-padded to 3 digits minimum)
        """
        from script.models.Account import Account
        from script.models.Base import database

        # If already assigned (e.g. retry after failure), reuse the same number
        if self.account.upload_post_username:
            self.account.add_cli(f'[UploadPost] Reusing existing profile number: {self.account.upload_post_username}')
            return self.account.upload_post_username

        # Atomically get the next number: find max existing number and add 1
        with database.atomic():
            # Use .cast('integer') for proper PostgreSQL CAST syntax
            # COALESCE handles the case where no accounts have a number yet (starts at 1)
            result = Account.select(
                fn.COALESCE(fn.MAX(Account.upload_post_username.cast('integer')), 0)
            ).where(
                Account.upload_post_username.is_null(False)
            ).scalar()

            next_number = int(result) + 1
            # Zero-pad to 3 digits minimum (001, 002, ..., 999, 1000, ...)
            profile_username = str(next_number).zfill(3)

            # Save to this account immediately so no other thread can get the same number
            self.account.upload_post_username = profile_username
            self.account.save()

        self.account.add_cli(f'[UploadPost] Assigned new profile number: {profile_username}')
        return profile_username

    def _create_profile(self, username):
        """
        Step 1: Create a user profile on Upload-Post.
        POST /api/uploadposts/users
        If the profile already exists, we log it and continue (not an error).
        """
        self.account.add_cli(f'[UploadPost] Creating profile for "{username}"...')

        response = requests.post(
            f'{UPLOAD_POST_BASE_URL}/uploadposts/users',
            headers=self.headers,
            json={'username': username},
        )

        data = response.json()

        if response.status_code == 200 and data.get('success'):
            self.account.add_cli(f'[UploadPost] Profile created successfully')
        elif response.status_code == 409 or 'already exists' in str(data).lower():
            # Profile already exists - that's fine, continue (retry scenario)
            self.account.add_cli(f'[UploadPost] Profile already exists, continuing...')
        else:
            raise Exception(f'Failed to create profile: {response.status_code} - {data}')

    def _generate_jwt(self, username):
        """
        Step 2: Generate a secure, single-use JWT access URL.
        POST /api/uploadposts/users/generate-jwt
        Returns the access_url that the user needs to visit in the browser.
        """
        self.account.add_cli(f'[UploadPost] Generating JWT access URL...')

        response = requests.post(
            f'{UPLOAD_POST_BASE_URL}/uploadposts/users/generate-jwt',
            headers=self.headers,
            json={'username': username},
        )

        data = response.json()

        if response.status_code == 200 and data.get('success'):
            access_url = data.get('access_url')
            self.account.add_cli(f'[UploadPost] Access URL generated (valid 48h)')
            return access_url

        raise Exception(f'Failed to generate JWT: {response.status_code} - {data}')

    def _open_access_url(self, access_url):
        """
        Step 3: Navigate the AdsPower browser to the Upload-Post connect page.
        After loading, we pause to let the page fully render before OAuth interaction.
        """
        self.account.add_cli(f'[UploadPost] Opening access URL in browser...')

        self.ig.page.goto(access_url, timeout=120000)
        self.ig.pause(6000, 10000)

        self.account.add_cli(f'[UploadPost] Connect page loaded')

    def _complete_oauth(self):
        """
        Step 4: Complete the OAuth flow on the Upload-Post connect page.

        Two possible flows after clicking "Connect Instagram":
          A) Account is already Business & previously connected -> direct Allow screen
          B) Account is Personal -> full Business conversion flow then Allow

        Each step is guarded by visibility checks so only the relevant screens are handled.
        """
        self.account.add_cli('[UploadPost] Starting OAuth flow...')

        # Step 4-pre: Check if Instagram is already connected on the Upload-Post page.
        # If the account username or disconnect button (X) is visible, it means
        # Instagram was already connected. Mark as connected and return early.
        disconnect_button = self.ig.page.locator('button[aria-label="Disconnect Instagram"]')
        if disconnect_button.is_visible():
            self.account.add_cli('[UploadPost] Instagram already connected on Upload-Post page, skipping OAuth')
            self._already_connected = True
            return

        # Step 4a: Click "Connect Instagram" button on Upload-Post connect page
        self.account.add_cli('[UploadPost] Clicking Connect Instagram button...')
        self.ig.page.get_by_role('button', name='Connect Instagram').click(timeout=20000)
        self.ig.pause(10000, 14000)

        # After clicking, Instagram redirects. Check what screen we landed on.
        self.account.add_cli(f'[UploadPost] Redirected to: {self.ig.page.url}')

        # --- Flow A: Direct Allow screen (already Business / previously connected) ---
        # If the account was connected before, Instagram shows a re-authorization screen.
        if self.ig.is_visible_by_text('Would you like to continue sharing'):
            self.account.add_cli('[UploadPost] Re-authorization screen detected (already connected before)')
            self.ig.page.get_by_role('button', name='Allow').click(timeout=10000)
            self.ig.pause(10000, 14000)
            self.account.add_cli(f'[UploadPost] OAuth flow completed, current URL: {self.ig.page.url}')
            return

        # --- Flow B: Full Business conversion flow (Personal account) ---

        # Step 4b: Click "Change" on convert_to_professional_account page
        if self.ig.is_visible_by_text('Change'):
            self.account.add_cli('[UploadPost] Clicking Change button...')
            self.ig.page.get_by_role('button', name='Change').click(timeout=10000)
            self.ig.pause(10000, 14000)

        # Step 4c: Select "Business" account type
        if self.ig.is_visible_by_text('Business'):
            self.account.add_cli('[UploadPost] Selecting Business account type...')
            self.ig.page.get_by_role('button', name='Business').first.click(timeout=10000)
            self.ig.pause(6000, 10000)

        # Step 4d: Click "Next" (first time)
        if self.ig.is_visible_by_text('Next'):
            self.account.add_cli('[UploadPost] Clicking Next (1)...')
            self.ig.page.get_by_role('button', name='Next').click(timeout=10000)
            self.ig.pause(6000, 10000)

        # Step 4e: Click "Next" (second time)
        if self.ig.is_visible_by_text('Next'):
            self.account.add_cli('[UploadPost] Clicking Next (2)...')
            self.ig.page.get_by_role('button', name='Next').click(timeout=10000)
            self.ig.pause(6000, 10000)

        # Step 4f: Category selection screen
        if self.ig.is_visible_by_text('Suggested'):
            self.account.add_cli('[UploadPost] Category selection screen detected...')

            # Check the "Show category on profile" checkbox
            show_category_checkbox = self.ig.page.locator('input[aria-label="Show category on profile"]')
            if show_category_checkbox.is_visible():
                show_category_checkbox.click(timeout=10000)
                self.ig.pause(2000, 4000)
                self.account.add_cli('[UploadPost] Checked "Show category on profile"')

            # Select a random category from the radio group
            import random
            category_buttons = self.ig.page.locator('[role="radiogroup"][name="category"] [role="button"]')
            count = category_buttons.count()

            if count > 0:
                random_index = random.randint(0, count - 1)
                selected = category_buttons.nth(random_index)
                category_name = selected.inner_text()
                selected.click(timeout=10000)
                self.ig.pause(2000, 4000)
                self.account.add_cli(f'[UploadPost] Selected category: {category_name}')
            else:
                self.account.add_cli('[UploadPost] No categories found')

            # Click "Done" to finish category selection
            if self.ig.is_visible_by_text('Done'):
                self.account.add_cli('[UploadPost] Clicking Done...')
                self.ig.page.get_by_role('button', name='Done').click(timeout=10000)
                self.ig.pause(6000, 10000)

        # Step 4g: Confirmation modal - Click "Continue"
        if self.ig.is_visible_by_text('Continue'):
            self.account.add_cli('[UploadPost] Clicking Continue...')
            self.ig.page.get_by_role('button', name='Continue').click(timeout=10000)
            self.ig.pause(6000, 10000)

        # Step 4h: Contact info screen - Click "Don't use my contact info"
        if self.ig.is_visible_by_text("Don't use my contact info"):
            self.account.add_cli("[UploadPost] Clicking Don't use my contact info...")
            self.ig.page.get_by_role('button', name="Don't use my contact info").click(timeout=10000)
            self.ig.pause(6000, 10000)

        # Step 4i: Final Done to complete Business conversion
        if self.ig.is_visible_by_text('Done'):
            self.account.add_cli('[UploadPost] Clicking final Done...')
            self.ig.page.get_by_role('button', name='Done').click(timeout=10000)
            self.ig.pause(6000, 10000)

        # Step 4j: OAuth permission screen - Click "Allow"
        if self.ig.is_visible_by_text('Allow'):
            self.account.add_cli('[UploadPost] Clicking Allow...')
            self.ig.page.get_by_role('button', name='Allow').click(timeout=10000)
            self.ig.pause(10000, 14000)

        # Wait for final redirect back to Upload-Post
        self.ig.pause(6000, 10000)

        self.account.add_cli(f'[UploadPost] OAuth flow completed, current URL: {self.ig.page.url}')

    def _verify_connection(self, username):
        """
        Step 6: Verify that the Instagram account is actually connected on Upload-Post.
        GET /api/uploadposts/users/{username}
        Checks if the 'instagram' field in social_accounts is not null/empty.
        Returns True if connected, False otherwise.
        """
        self.account.add_cli(f'[UploadPost] Verifying connection for profile "{username}"...')

        response = requests.get(
            f'{UPLOAD_POST_BASE_URL}/uploadposts/users/{username}',
            headers=self.headers,
        )

        data = response.json()

        if response.status_code == 200 and data.get('success'):
            social_accounts = data.get('profile', {}).get('social_accounts', {})
            instagram = social_accounts.get('instagram')

            # instagram is null or empty string when not connected
            if instagram and instagram != '':
                self.account.add_cli(f'[UploadPost] Verified: Instagram is connected')
                return True

            self.account.add_cli(f'[UploadPost] Verified: Instagram is NOT connected')
            return False

        self.account.add_cli(f'[UploadPost] Verify API call failed: {response.status_code}')
        return False

    # -------------------------------------------------------------------------
    # Disconnect flow
    # -------------------------------------------------------------------------

    def _disconnect(self):
        """
        Disconnect flow: delete the profile from Upload-Post via API and reset local status.
        No browser interaction needed - deleting the profile removes Upload-Post's ability
        to publish. The Instagram OAuth permission remains but is harmless.
        upload_post_username is NOT cleared - numbers are never reused.
        On failure, reverts to original status so worker can retry.
        """
        # Remember original status so we can revert on failure
        original_status = self.account.upload_post_status

        try:
            profile_username = self.account.upload_post_username

            if not profile_username:
                self.account.add_cli('[UploadPost] No profile username assigned, nothing to disconnect')
                self._update_status('none')
                return

            self.account.add_cli(f'[UploadPost] Deleting profile "{profile_username}" via API...')

            response = requests.delete(
                f'{UPLOAD_POST_BASE_URL}/uploadposts/users',
                headers=self.headers,
                json={'username': profile_username},
            )

            # Safety check: API might return empty response or non-JSON
            if response.text.strip():
                data = response.json()
            else:
                data = {}

            if response.status_code == 200 and data.get('success'):
                self._update_status('none')
                self.account.add_cli(f'[UploadPost] Profile deleted, status reset to none')
            elif response.status_code == 404:
                # Profile didn't exist on Upload-Post anyway, just reset local status
                self._update_status('none')
                self.account.add_cli(f'[UploadPost] Profile not found on Upload-Post, resetting to none')
            else:
                # Revert to original status so worker can retry
                self._update_status(original_status)
                self.account.add_cli(f'[UploadPost] Disconnect failed: {response.status_code} - {data} - reverted to "{original_status}"')

        except Exception as e:
            # Revert to original status so worker can retry
            self._update_status(original_status)
            self.account.add_cli(f'[UploadPost] Disconnect error: {str(e)} - reverted to "{original_status}"')

    # -------------------------------------------------------------------------
    # Suspended account cleanup
    # -------------------------------------------------------------------------

    def _cleanup_one_suspended_profile(self):
        """
        Find one suspended account that has an Upload-Post profile and delete it.

        Uses atomic UPDATE ... WHERE ... LIMIT 1 to prevent race conditions
        when multiple workers run simultaneously. Each worker picks a different
        suspended account to clean up.

        Only clears upload_post_status to 'none'. upload_post_username is kept
        in case the account becomes active again and needs to reconnect with
        the same profile number.
        """
        from script.models.Account import Account
        from script.models.Base import database

        try:
            with database.atomic():
                # Atomically claim one suspended account that has an Upload-Post profile
                suspended = (Account
                    .select()
                    .where(
                        (Account.instagram_state == 'suspended') &
                        (Account.upload_post_username.is_null(False)) &
                        (Account.upload_post_status != 'none')
                    )
                    .order_by(Account.id)
                    .limit(1)
                    .for_update()
                    .first())

                if not suspended:
                    return

                self.account.add_cli(f'[UploadPost Cleanup] Found suspended account: {suspended.username} (ID: {suspended.id})')

                # Delete the profile from Upload-Post API
                profile_username = suspended.upload_post_username

                response = requests.delete(
                    f'{UPLOAD_POST_BASE_URL}/uploadposts/users',
                    headers=self.headers,
                    json={'username': profile_username},
                )

                # Reset status to 'none' but keep upload_post_username
                suspended.upload_post_status = 'none'
                suspended.save()

                self.account.add_cli(f'[UploadPost Cleanup] Deleted profile "{profile_username}" for suspended account {suspended.username}')

        except Exception as e:
            self.account.add_cli(f'[UploadPost Cleanup] Error: {str(e)}')



    def _update_status(self, status):
        """
        Update the upload_post_status field on the account and persist to database.
        """
        self.account.upload_post_status = status
        self.account.save()