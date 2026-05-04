from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
from script.extra.helper import *
import shutil
import re
import random
import time
from script.extra.helper import go_to_page, tehran_now
from script.models.Setting import Setting
from script.models.Lead import Lead
from script.models.AccountTemplate import AccountTemplate
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# How long to wait for the Instagram media/configure response after Share.
# The capture happens in a background listener; this is the upper bound
# for the wait_for_post_url loop.
POST_URL_CAPTURE_TIMEOUT = 70


class BrowserPostMediaEvent:
    base = None
    command = 0
    templates = None
    template_type = None
    image_path = None
    video_path = None
    lead = None
    caption = 0
    tmp = 0
    media_list_types = ['image-post', 'video-post', 'carousel']

    # Custom flow state. is_custom_post drives the branching in the
    # after-hook; account_template_record is the row we claimed (and
    # must update on success or release on failure).
    is_custom_post = False
    account_template_record = None

    # Captured post URL and listener state. Populated asynchronously
    # by the response listener attached around the Share click.
    post_url = None
    _post_url_listener = None

    def __init__(self, ig):
        self.ig = ig
        self.posting_age = int(Setting.get_value("allowed_posting_age"))

    def init(self):
        # The 2-day account age guard applies to every post type.
        # Younger accounts cannot post regardless of custom or Lead flow.
        if self.ig.account.get_passed_days_since_creation() < 2:
            raise Exception(f"Account is not old enough to Post Media")

        self.ig.account.add_cli(f"[BrowserPostMediaEvent] Allowed posting age : {self.posting_age}", print_only=True)

        # Allowed-posting-age setting is skipped for custom posts because
        # the user explicitly assigned them; the worker should run the
        # job as soon as the account is otherwise eligible.
        # We resolve the path first so we know whether this run is custom
        # before deciding whether to enforce the setting.
        self.ig.account.add_cli(f"[BrowserPostMediaEvent] Posting a media ...")

        try:
            self.turn_on_notif()
            self.generate_path()

            if not self.is_custom_post:
                if self.ig.account.get_passed_days_since_creation() < self.posting_age:
                    return self.ig.account.add_cli(f"[BrowserPostMediaEvent] Account is not old enough to post image")

            self.generate_caption()
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"[BrowserPostMediaEvent] Problem Posting Image : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

            # If we claimed a custom assignment but never made it to
            # after_change_hook, return it to pending so another run
            # can retry it. Without this the row stays in 'processing'
            # forever and is invisible to both workers and stats.
            self._release_custom_claim_on_failure()

        finally:
            self._remove_post_url_listener()

            if self.tmp:
                shutil.rmtree(self.tmp)
            go_to_page(self.ig, "https://www.instagram.com/", "Home")
            self.ig.pause(3000, 4000)

    def generate_path(self):
        """
        Resolve which templates this run will post.
        Custom assignments win over Lead-based picks: if this account
        has a pending custom row, we claim it and use its template.
        Otherwise we fall back to the original Lead.get_a_media flow.
        """
        self.tmp = generate_random_folder()

        custom_template, at_record = self.ig.account.get_pending_custom_template()

        if custom_template:
            self._setup_from_custom(custom_template, at_record)
        else:
            self._setup_from_lead()

        self._download_templates()

    def _setup_from_custom(self, template, at_record):
        """
        Build self.templates from a single claimed custom template.
        For video-post we resolve the cover image via carousel_id;
        for carousel we expand to all slides ordered by uid.
        """
        from script.models.Template import Template

        self.is_custom_post = True
        self.account_template_record = at_record
        self.template_type = template.type
        self.lead = None

        self.ig.account.add_cli(
            f"[BrowserPostMediaEvent] Custom assignment claimed: "
            f"template #{template.id} type={template.type}"
        )

        if template.type == 'video-post':
            # The assigned record always points at the video sub_type.
            # Pull the matching cover image from the same carousel_id.
            image_template = (
                Template
                .select()
                .where(
                    (Template.carousel_id == template.carousel_id) &
                    (Template.sub_type == 'image') &
                    (Template.type == 'video-post')
                )
                .first()
            )

            self.templates = [t for t in [image_template, template] if t]

        elif template.type == 'carousel':
            slides = list(
                Template
                .select()
                .where(Template.carousel_id == template.carousel_id)
                .order_by(Template.uid)
            )
            self.templates = slides if slides else [template]

        else:
            self.templates = [template]

    def _setup_from_lead(self):
        """Original Lead-based template selection."""
        self.templates, self.template_type, self.lead = Lead.get_a_media(
            self.ig.account, self.media_list_types
        )

        if not self.templates:
            raise Exception("We don't have any media for this account  ...")

    def _download_templates(self):
        """
        Download (and for images, post-process) every template in the
        current set. Mirrors the original branching: video-post handles
        image and video sub_types separately; everything else processes
        all entries as images.
        """
        if self.template_type == 'video-post':

            for template in self.templates:
                template.path = template.download_image(self.tmp)

                if template.sub_type == 'video':
                    self.video_path = template.path
                    self.ig.account.add_cli(
                        f"[BrowserPostMediaEvent] video path : {template.path} "
                        f"Sub type: {template.sub_type} for {self.template_type}")

                elif template.sub_type == 'image':
                    self.image_path = process_image(template.path, self.tmp)
                    self.ig.account.add_cli(
                        f"[BrowserPostMediaEvent] image path : {template.path} "
                        f"Sub type: {template.sub_type} for {self.template_type}")

        else:

            for template in self.templates:
                template.path = template.download_image(self.tmp)
                template.path = process_image(template.path, self.tmp)

                self.ig.account.add_cli(f"[BrowserPostMediaEvent] image path : {template.path} for {self.template_type}")

    def generate_caption(self):
        self.ig.account.add_cli(f'[BrowserPostMediaEvent] Caption is {self.templates[0].caption}')
        self.caption = self.templates[0].caption

    def before_change_hook(self):
        self.ig.account.set_state('post image', 'app_state')
        self.command = self.ig.account.create_command('post media', 'processing')

    def change_hook(self):
        try:
            self.ig.page.get_by_role("link", name="New post Create").click(timeout=4000)
        except:
            self.ig.page.get_by_role("link", name="New post").click(timeout=4000)

        self.ig.pause(3000, 4000)

        try:
            self.ig.page.locator('svg[aria-label="Post"]').click(timeout=3000)
        except Exception as e:
            try:
                self.ig.account.add_cli(f"[BrowserPostMediaEvent] Post button doesnt exists : {str(e)}")
                self.ig.page.locator('a[href="#"]:has(svg[aria-label="Post"])').click(timeout=3000)
            except Exception as e:
                pass

        self.ig.pause(3000, 3500)

        if self.template_type == 'video-post':
            self.locate_media_path(self.video_path)

        else:

            clicked_on_filter = False

            for template in self.templates:
                self.locate_media_path(template.path)

                if self.template_type == 'carousel' and not clicked_on_filter:
                    self.ig.pause(2000, 2700)
                    self.ig.page.locator("button").filter(has_text="Open media gallery").click()
                    clicked_on_filter = True

                self.ig.pause(4000, 4500)

        self.ig.pause(3000, 3500)

        try:
            self.ig.page.get_by_role("button", name="OK").click(timeout=3000)
        except:
            pass
        self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").first.click()
        self.ig.pause(2000, 3500)

        if self.template_type == 'video-post' and self.image_path:
            self.ig.page.locator('div.html-div.xdj266r.x14z9mp>div>form input[accept="image/jpeg,image/png"]').nth(
                0).set_input_files(self.image_path)
            self.ig.page.locator('input[accept="image/jpeg,image/png"]').nth(0).set_input_files(self.image_path)
            self.ig.pause(2000, 3500)

        self.ig.page.get_by_role("button", name="Next").first.click()
        self.ig.pause(2000, 3500)

        if self.caption:
            self.ig.page.get_by_label("Write a caption...").fill(self.caption)
            self.ig.pause(3000, 4500)

        # Attach the response listener BEFORE clicking Share so the
        # media/configure response (which carries the post code) is
        # not missed. The listener runs in the background and stores
        # the URL in self.post_url; wait_for_reel_shared still owns
        # the user-visible confirmation.
        self._setup_post_url_listener()

        self.ig.page.get_by_role("button", name="Share").click()

        if self.wait_for_reel_shared():
            self.ig.account.add_cli("[BrowserPostMediaEvent] Reel shared confirmation received")
        else:
            self.ig.account.add_cli("[BrowserPostMediaEvent] Reel share confirmation NOT detected")

        # Give the listener a brief grace period in case the response
        # arrives slightly after the success banner. Bounded by the
        # constant at the top of this file.
        self._wait_for_post_url()

    def locate_media_path(self, path):
        try:
            self.ig.page.locator(
                "input[accept='image/avif,image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(path)
        except:
            self.ig.page.locator(
                "input[accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").nth(
                0).set_input_files(path)

    def wait_for_reel_shared(self, timeout_sec=70):
        import time

        start = time.time()

        while time.time() - start < timeout_sec:
            # if self.ig.is_visible_by_text('Your post could not be shared'):
            #     self.ig.page.get_by_role('button', name=re.compile(r'Try again', re.IGNORECASE)).click(timeout=3000)
            #     self.ig.pause(4000, 5000)
            try:
                if self.ig.is_visible_by_text('Your reel has been shared') or self.ig.is_visible_by_text(
                        'Your post has been shared'):
                    return True
            except TimeoutError:
                pass

            self.ig.account.add_cli("[BrowserPostMediaEvent] Post hasn't been posted yet ...")
            time.sleep(5)

        return False

    def after_change_hook(self):
        """
        Finalize the run.
        Custom posts already have a row in 'processing' that just needs
        to be completed with the captured URL and a fresh timestamp.
        Non-custom posts get one fresh 'completed' row representing the
        actual post on Instagram (one record per real post regardless
        of how many templates were attached, e.g. carousel slides).
        """
        self.command.update_cmd('state', 'success')
        self.ig.account.add_cli("[BrowserPostMediaEvent] Media posted successfully")

        if self.lead and self.lead.account is None:
            self.lead.set_account(self.ig.account)

        if self.is_custom_post:
            self._complete_custom_record()
        else:
            self._attach_primary_template()

    def _complete_custom_record(self):
        """
        Move the claimed account_template row from 'processing' to
        'completed' and store the captured URL. created_at is bumped
        to the actual post time so it doubles as the post timestamp.
        """
        if not self.account_template_record:
            return

        now = tehran_now()

        AccountTemplate.update(
            status='completed',
            url=self.post_url,
            created_at=now,
            updated_at=now,
        ).where(
            AccountTemplate.id == self.account_template_record.id
        ).execute()

        self.ig.account.add_cli(
            f"[BrowserPostMediaEvent] Custom record #{self.account_template_record.id} "
            f"completed url={self.post_url}"
        )

    def _attach_primary_template(self):
        """
        For non-custom posts, create exactly one account_template row.
        We pick the primary template per type so a carousel does not
        produce multiple stat rows for what is a single Instagram post:
          - image-post: the only template
          - video-post: the video sub_type record
          - carousel:   the first slide ordered by uid
        """
        primary = self._pick_primary_template()

        if not primary:
            self.ig.account.add_cli(
                "[BrowserPostMediaEvent] No primary template to attach"
            )
            return

        self.ig.account.attach_template(primary, url=self.post_url)
        self.ig.account.add_cli(
            f"[BrowserPostMediaEvent] Non-custom record created for "
            f"template #{primary.id} url={self.post_url}"
        )

    def _pick_primary_template(self):
        """Single primary template per real post; see _attach_primary_template."""
        if not self.templates:
            return None

        if self.template_type == 'video-post':
            for t in self.templates:
                if getattr(t, 'sub_type', None) == 'video':
                    return t
            return self.templates[0]

        if self.template_type == 'carousel':
            slides = sorted(
                self.templates,
                key=lambda t: (getattr(t, 'uid', None) or '')
            )
            return slides[0]

        return self.templates[0]

    def turn_on_notif(self):
        import re
        if self.ig.is_visible_by_text('Turn On notif'):
            try:
                self.ig.page.get_by_role('button', name=re.compile(r'Turn On', re.IGNORECASE)).click()
                self.ig.pause(4000, 5000)
            except:
                self.ig.account.add_cli("[BrowserPostMediaEvent] Turn On doesn't exists")
                pass

    def _setup_post_url_listener(self):
        """
        Install a response listener that watches for Instagram's
        media/configure family of endpoints. The same code field is
        present in all three:
          - image-post:  /api/v1/media/configure/
          - video-post:  /api/v1/media/configure_to_clips/
          - carousel:    /api/v1/media/configure_sidecar/
        """
        if self._post_url_listener is not None:
            return

        def on_response(response):
            # Already captured for this run; ignore subsequent matches.
            if self.post_url:
                return

            try:
                url = response.url

                if '/api/v1/media/configure' not in url:
                    return

                if response.status != 200:
                    return

                data = response.json()
                media = data.get('media') or {}
                code = media.get('code')

                if code:
                    self.post_url = f"https://www.instagram.com/p/{code}/"
                    self.ig.account.add_cli(
                        f"[BrowserPostMediaEvent] Captured post URL: {self.post_url}"
                    )

            except Exception as e:
                self.ig.account.add_cli(
                    f"[BrowserPostMediaEvent] URL listener error: {str(e)}"
                )

        self._post_url_listener = on_response
        self.ig.page.on('response', self._post_url_listener)

    def _remove_post_url_listener(self):
        """Detach the listener; safe to call multiple times."""
        if self._post_url_listener is None:
            return

        try:
            self.ig.page.remove_listener('response', self._post_url_listener)
        except Exception:
            pass

        self._post_url_listener = None

    def _wait_for_post_url(self):
        """
        Poll up to POST_URL_CAPTURE_TIMEOUT seconds for the listener
        to populate self.post_url. Returns immediately if already set.
        Missing URL is non-fatal: the post itself succeeded, only the
        stats link is unavailable.
        """
        if self.post_url:
            return

        start = time.time()
        last_log = start

        while time.time() - start < POST_URL_CAPTURE_TIMEOUT:
            if self.post_url:
                elapsed = round(time.time() - start, 1)
                self.ig.account.add_cli(
                    f"[BrowserPostMediaEvent] URL captured in {elapsed}s after share"
                )
                return

            now = time.time()
            if now - last_log >= 10:
                self.ig.account.add_cli(
                    f"[BrowserPostMediaEvent] Waiting for post URL ({int(now - start)}s)"
                )
                last_log = now

            time.sleep(0.3)

        self.ig.account.add_cli(
            "[BrowserPostMediaEvent] Post URL was not captured within timeout"
        )

    def _release_custom_claim_on_failure(self):
        """
        Return a claimed custom row to 'pending' so a future run can
        retry it. Only acts when this run is custom and we have not
        already completed the record.
        """
        if not self.is_custom_post or not self.account_template_record:
            return

        try:
            AccountTemplate.update(
                status='pending',
                updated_at=tehran_now(),
            ).where(
                (AccountTemplate.id == self.account_template_record.id) &
                (AccountTemplate.status == 'processing')
            ).execute()

            self.ig.account.add_cli(
                f"[BrowserPostMediaEvent] Released custom claim "
                f"#{self.account_template_record.id} back to pending"
            )
        except Exception as e:
            self.ig.account.add_cli(
                f"[BrowserPostMediaEvent] Failed to release custom claim: {str(e)}"
            )