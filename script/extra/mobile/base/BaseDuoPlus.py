import os
import re
import time
import xml.etree.ElementTree as ET
from script.models.Proxy import _get_free_proxy

import requests
from dotenv import load_dotenv

load_dotenv()


class DuoPlusApiError(RuntimeError):
    """Top-level API failure (bad key, IP not whitelisted, malformed request)."""


class DeviceCommandError(RuntimeError):
    """The device accepted the request but reported failure for the command."""


class MobileUnusable(Exception):
    """
    The phone is in a dead-end DuoPlus status (0/3/4/12) and no amount of
    polling will fix it. The caller should set app_state=error and skip.
    """


class BaseDuoPlus:
    """
    Execution layer for one DuoPlus cloud phone — the mobile mirror of
    BasePlaywright. Everything the modules need (tap/type/dump/find/launch)
    goes through here; no module talks to the HTTP API directly.

    Design constraints baked in (from the DuoPlus docs + real debug runs):
      * Hard rate limit of 1 request/sec per interface, so every call is
        followed by a fixed pause. A full UI dump is TWO calls
        (DuoPlusDumpUI, then cat) — budget timings accordingly.
      * DuoPlus often returns HTTP 200 with a non-200 "code" in the body, so
        raise_for_status() alone won't catch errors; the body is always
        checked. Body code 512 means "busy / repeat operation" and is retried
        with backoff.
      * An API "OK" does not guarantee the action actually happened on screen
        (app/start returned OK in testing while the phone sat on the
        launcher). Anything that matters is verified via foreground_activity
        or a dump, never trusted blindly.
      * Commands must finish within 10 seconds on the device side, which is
        why screenshots ride back as base64 and dumps are two-step.
      * No parallelism within one phone: one worker process per mobile, all
        calls sequential.

    powerOn and status are batch endpoints (up to 100 phones), so they are
    classmethods taking a list of duo_ids; per-instance boot_mobile() uses
    them for its own single phone.
    """

    API_BASE = os.getenv('DUOPLUS_API_BASE', 'https://openapi.duoplus.net')

    COMMAND_PATH = '/api/v1/cloudPhone/command'
    APP_START_PATH = '/api/v1/app/start'
    POWER_ON_PATH = '/api/v1/cloudPhone/powerOn'
    STATUS_PATH = '/api/v1/cloudPhone/status'

    # QPS=1 per interface; 1.6s proved reliable in the login test script
    # (1.2s occasionally tripped 512s under load).
    # DuoPlus documents a hard 1 request/sec limit per interface. 1.25s keeps
    # a safety margin above that line — 1.05 was too tight and risked 160004
    # ("too frequent") errors that stall page loads. Lower cautiously only if
    # the panel proves it tolerates it.
    RATE_LIMIT_PAUSE = 1.25

    DUMP_PATH_ON_DEVICE = '/sdcard/_worker_ui.xml'
    SHOT_PATH_ON_DEVICE = '/sdcard/_worker_shot.png'

    INSTAGRAM_PKG = 'com.instagram.android'

    # Packages a VIEW intent can leak into when Android ignores the pinned
    # package (observed once in phase-8 dumps: a story URL opened in Chrome).
    # Used to classify "the link went to a browser" as a retryable failure.
    BROWSER_PKGS = (
        'com.android.chrome',
        'com.chrome.beta',
        'org.chromium.webview_shell',
        'com.sec.android.app.sbrowser',
        'org.mozilla.firefox',
        'com.android.browser',
    )
    # 800ms proved too short on a real device (Instagram's account switcher
    # did not open); 1200ms registers reliably.
    LONG_PRESS_MS = 1200

    # Instagram activity names (the suffix returned by foreground_activity_name).
    # These live on the device layer because foreground detection lives here and
    # both the login and explore events compare against them. IG activity paths
    # vary between builds, but these trailing class names are stable.
    ACT_HOME = 'MainTabActivity'
    ACT_HOME_ALT = 'InstagramMainActivity'
    ACT_MODAL = 'ModalActivity'
    ACT_CHALLENGE = 'ChallengeActivity'   # suspended / challenge screen
    HOME_ACTIVITIES = (ACT_HOME, ACT_HOME_ALT)

    BOOT_TIMEOUT_SECONDS = 120
    BOOT_POLL_INTERVAL = 5

    BOUNDS_RE = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')

    def __init__(self, mobile):
        """
        `mobile` is the peewee Mobile row. Only duo_id is strictly required,
        so tests can pass a lightweight stub with a duo_id attribute.

        This object is the mobile analogue of the web `ig`: it bundles the
        device primitives with the current session's account. SessionRunner
        sets `account` at the start of each per-account session; contexts and
        events read it as `device.account`, exactly like the web side reads
        `ig.account`.
        """
        self.mobile = mobile
        self.phone_id = mobile.duo_id
        self.account = None  # set per-session by SessionRunner
        self._launcher_component = None  # resolved once, then cached

    def pause(self, min_ms, max_ms):
        """Random human-ish pause, mirroring BasePlaywright.pause()."""
        import random
        time.sleep(random.randint(min_ms, max_ms) / 1000.0)

    # ── low-level HTTP plumbing ─────────────────────────────────────────────
    @classmethod
    def _headers(cls):
        api_key = os.getenv('DUOPLUS_API_KEY')
        if not api_key:
            raise DuoPlusApiError('DUOPLUS_API_KEY is not set in env')
        return {'DuoPlus-API-Key': api_key, 'Content-Type': 'application/json'}

    @classmethod
    def _post(cls, path, payload, retries=4):
        """
        One API call with rate-limit pause, 512 backoff and body-error checks.
        Returns the parsed JSON body. Raises DuoPlusApiError on hard failures.
        """
        url = f'{cls.API_BASE}{path}'
        last_err = None

        for attempt in range(retries):
            print(url)
            print(cls._headers())
            print(payload)
            resp = requests.post(
                url,
                headers=cls._headers(),
                json=payload,
                timeout=30)
            # The pause comes right after the request so even error paths
            # respect the QPS=1 limit.
            time.sleep(cls.RATE_LIMIT_PAUSE)
            resp.raise_for_status()
            data = resp.json()

            code = data.get('code')
            if code == 512:
                # Busy / repeat operation: linear backoff, then retry.
                wait = 3 * (attempt + 1)
                print(f'[duoplus] API busy (512), waiting {wait}s ...')
                time.sleep(wait)
                last_err = data.get('message')
                continue

            if code not in (200, None):
                raise DuoPlusApiError(
                    f'API error code={code} message={data.get("message")!r}'
                )

            return data

        raise DuoPlusApiError(f'API kept returning 512 after {retries} tries ({last_err})')

    def command(self, cmd, want_output=False, retries=4):
        """
        Run one Android shell command on this phone. Returns the command's
        text output (data[phone_id].content) if want_output, else True.
        """
        data = self._post(
            self.COMMAND_PATH,
            {'image_ids': [self.phone_id], 'command': cmd},
            retries=retries,
        )

        phone = (data.get('data') or {}).get(self.phone_id)
        if not phone:
            raise DuoPlusApiError(
                f'no result for phone {self.phone_id!r}. '
                f'Check the phone id and that ADB/API is enabled. '
                f'Raw: {str(data)[:200]}'
            )
        if not phone.get('success'):
            raise DeviceCommandError(
                f'device failed {cmd!r}: {phone.get("message") or "no message"}'
            )
        return phone.get('content', '') if want_output else True

    # ── batch endpoints (up to 100 phones per call) ─────────────────────────
    @classmethod
    def batch_status(cls, duo_ids):
        """
        Fetch DuoPlus statuses for many phones in one call.
        Returns {duo_id: int_status_code} for whatever the API reported.

        The payload shape is not fully pinned down (observed variants nest the
        records under a wrapper key, e.g. data.list = [{id, status}, ...]), so
        the response is walked recursively and any record that mentions one of
        the requested duo_ids together with a status is picked up. Anything the
        API didn't report simply won't be in the returned dict — callers
        already treat a missing duo_id as "unknown".
        """
        data = cls._post(cls.STATUS_PATH, {'image_ids': list(duo_ids)})

        result = {}
        cls._collect_statuses(data.get('data'), set(duo_ids), result)
        return result

    # Field names seen (or plausible) across DuoPlus payloads for the phone id
    # and its status. Checked in order.
    _ID_KEYS = ('image_id', 'imageId', 'phone_id', 'phoneId',
                'cloud_phone_id', 'cloudPhoneId', 'id')
    _STATUS_KEYS = ('status', 'state', 'phone_status', 'phoneStatus',
                    'cloudPhoneStatus')

    # Fallback when a payload returns the human-readable label instead of the
    # numeric code (the panel shows these strings).
    _STATUS_NAMES = {
        'not configured': 0,
        'powered on': 1,
        'powered off': 2,
        'expired': 3,
        'renewal needed': 4,
        'powering on': 10,
        'configuring': 11,
        'configuration failed': 12,
    }

    @classmethod
    def _coerce_status(cls, value):
        """Turn a raw status value (int, '1', 'Powered On') into a code, or None."""
        if isinstance(value, bool) or value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.lstrip('-').isdigit():
                return int(text)
            return cls._STATUS_NAMES.get(text.lower())
        return None

    @classmethod
    def _status_from_record(cls, record):
        for key in cls._STATUS_KEYS:
            if key in record:
                code = cls._coerce_status(record[key])
                if code is not None:
                    return code
        return None

    @classmethod
    def _collect_statuses(cls, block, wanted_ids, result):
        """
        Walk an arbitrary response fragment and fill `result` with any
        {duo_id: status} pairs found. Handles: a mapping keyed by duo_id (value
        either a bare code or an object), a list of record objects, and records
        nested under one or more wrapper keys.
        """
        if isinstance(block, list):
            for item in block:
                cls._collect_statuses(item, wanted_ids, result)
            return

        if not isinstance(block, dict):
            return

        # Case 1: this dict is itself a record, e.g. {"id": "gcsTe", "status": 1}
        for id_key in cls._ID_KEYS:
            duo_id = block.get(id_key)
            if isinstance(duo_id, str) and duo_id in wanted_ids:
                code = cls._status_from_record(block)
                if code is not None:
                    result[duo_id] = code
                break

        # Case 2: mapping keyed by duo_id, and/or wrapper keys to recurse into.
        for key, value in block.items():
            if isinstance(key, str) and key in wanted_ids:
                code = (cls._status_from_record(value)
                        if isinstance(value, dict) else cls._coerce_status(value))
                if code is not None:
                    result[key] = code
                continue

            if isinstance(value, (dict, list)):
                cls._collect_statuses(value, wanted_ids, result)

    @classmethod
    def batch_power_on(cls, duo_ids):
        """
        Batch async power-on. Returns True if the API accepted the request —
        the phones are NOT on yet; the caller must poll batch_status().
        """
        cls._post(cls.POWER_ON_PATH, {'image_ids': list(duo_ids)})
        return True

    # ── boot / power (phase 3) ──────────────────────────────────────────────
    def get_status(self):
        """Status of this one phone (still goes through the batch endpoint)."""
        statuses = self.batch_status([self.phone_id])
        return statuses.get(self.phone_id, -1)

    def boot_mobile(self):
        """
        Startup recovery only — the fleet policy is always-on and there is
        deliberately no powerOff anywhere (not per-cycle, not in finally).

          status 1        -> ready, return
          status 2        -> powerOn, then poll until 1 (or timeout)
          status 10/11    -> already coming up, just poll
          status 0/3/4/12 -> dead end, raise MobileUnusable

        Every observed status is written back to mobiles.status so the panel
        stays honest even between central sync runs.
        """
        from script.models.Mobile import Mobile

        st = self.get_status()
        self._record_status(st)

        if st == Mobile.STATUS_ON:
            return True

        if st in Mobile.UNUSABLE_STATUSES or st == -1:
            raise MobileUnusable(f'phone {self.phone_id} unusable, status={st}')

        if st == Mobile.STATUS_OFF:
            print(f'[duoplus] phone {self.phone_id} is off, powering on ...')
            self.batch_power_on([self.phone_id])

        # STATUS_OFF (after powerOn), STATUS_POWERING_ON and STATUS_CONFIGURING
        # all land here: poll until on, unusable, or timeout.
        deadline = time.time() + self.BOOT_TIMEOUT_SECONDS
        while time.time() < deadline:
            time.sleep(self.BOOT_POLL_INTERVAL)
            st = self.get_status()
            self._record_status(st)

            if st == Mobile.STATUS_ON:
                print(f'[duoplus] phone {self.phone_id} is up')
                return True
            if st in Mobile.UNUSABLE_STATUSES:
                raise MobileUnusable(f'phone {self.phone_id} became unusable, status={st}')

        raise MobileUnusable(
            f'phone {self.phone_id} did not power on within '
            f'{self.BOOT_TIMEOUT_SECONDS}s (last status={st})'
        )

    def _record_status(self, status_code):
        # Best-effort: a stub mobile in tests may not have set_status.
        if hasattr(self.mobile, 'set_status'):
            try:
                self.mobile.set_status(status_code)
            except Exception as e:
                print(f'[duoplus] could not persist status: {e}')

    # ── input primitives ────────────────────────────────────────────────────
    def tap(self, x, y):
        self.command(f'input tap {int(x)} {int(y)}')

    def double_tap(self, x, y):
        """
        Double-tap, used by Instagram as the "like" gesture.

        Both taps go in a single shell command on purpose: sending them as two
        API calls would space them ~1.6s apart because of the rate limit, and
        Android would see two independent taps rather than a double-tap.
        """
        self.command(f'input tap {int(x)} {int(y)} && input tap {int(x)} {int(y)}')

    def long_press(self, x, y, ms=None):
        ms = ms or self.LONG_PRESS_MS
        # A zero-distance swipe with a duration is the standard long-press.
        self.command(f'input swipe {int(x)} {int(y)} {int(x)} {int(y)} {int(ms)}')

    def swipe_up(self, distance=800, duration_ms=300):
        # Center-ish coordinates; resolution differences don't matter much
        # for a generic scroll gesture.
        self.command(f'input swipe 540 1400 540 {1400 - distance} {duration_ms}')

    def swipe_down(self, distance=800, duration_ms=300):
        self.command(f'input swipe 540 600 540 {600 + distance} {duration_ms}')

    def type_text(self, text):
        """
        Type text into the currently focused field. `input text` cannot take
        raw spaces (%s is the ADB convention) and shell metacharacters must be
        escaped or the command endpoint mangles them.
        """
        escaped = (
            text
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace('&', '\\&')
            .replace('$', '\\$')
            .replace('(', '\\(')
            .replace(')', '\\)')
            .replace('<', '\\<')
            .replace('>', '\\>')
            .replace('|', '\\|')
            .replace(';', '\\;')
            .replace(' ', '%s')
        )
        self.command(f'input text "{escaped}"')

    def clear_field(self, max_chars=30):
        """
        Clear the focused field in ONE API call: MOVE_END followed by a batch
        of DELs in a single keyevent (keyevent accepts a sequence of codes).
        Fewer calls matters against the 1 req/sec limit. 30 chars covers the
        longest field we type (a share_group_NN name is ~14).
        """
        seq = ['123'] + ['67'] * max_chars  # 123 = MOVE_END, 67 = DEL
        self.command(f'input keyevent {" ".join(seq)}')

    def press_back(self):
        self.command('input keyevent 4')

    def press_enter(self):
        self.command('input keyevent 66')

    # ── UI dump & selectors ─────────────────────────────────────────────────
    def dump_xml(self):
        """
        Capture the UI hierarchy. Two steps by necessity: DuoPlusDumpUI writes
        the file on-device (it works on dynamic pages where the native
        uiautomator dump fails), then cat reads it back. Costs ~2 API calls
        plus the pauses — treat dumps as expensive.
        """
        self.command(f'DuoPlusDumpUI {self.DUMP_PATH_ON_DEVICE}')
        # Brief settle so the file is fully written before we cat it. 0.5s is
        # enough in practice; the RATE_LIMIT_PAUSE between the two calls adds
        # more on top.
        time.sleep(0.5)
        return self.command(f'cat {self.DUMP_PATH_ON_DEVICE}', want_output=True) 

    def find(self, xml_text, selector):
        """
        Find the first node matching the selector and return its tap point.

        selector keys (any combination, all must match):
          rid  -> resource-id, matched by suffix (ids are pkg-qualified)
          text -> exact text match
          desc -> content-desc, matched by prefix (IG appends dynamic parts)

        Returns (x, y, node) of the bounds center, or None.
        """
        if not xml_text:
            return None
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return None

        for node in root.iter('node'):
            attrs = node.attrib

            if 'rid' in selector:
                rid = attrs.get('resource-id', '')
                if not rid.endswith(selector['rid']):
                    continue
            if 'text' in selector:
                if attrs.get('text', '') != selector['text']:
                    continue
            if 'desc' in selector:
                if not attrs.get('content-desc', '').startswith(selector['desc']):
                    continue

            m = self.BOUNDS_RE.match(attrs.get('bounds', ''))
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            return (x1 + x2) // 2, (y1 + y2) // 2, node

        return None

    def find_all(self, xml_text, selector):
        """
        Like find() but returns EVERY matching node as (x, y, node) tuples.
        Needed by flows that read repeated rows/tiles (e.g. the share sheet's
        group grid) instead of a single control.
        """
        results = []
        if not xml_text:
            return results
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return results

        for node in root.iter('node'):
            attrs = node.attrib

            if 'rid' in selector:
                rid = attrs.get('resource-id', '')
                if not rid.endswith(selector['rid']):
                    continue
            if 'text' in selector:
                if attrs.get('text', '') != selector['text']:
                    continue
            if 'desc' in selector:
                if not attrs.get('content-desc', '').startswith(selector['desc']):
                    continue

            m = self.BOUNDS_RE.match(attrs.get('bounds', ''))
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            results.append(((x1 + x2) // 2, (y1 + y2) // 2, node))

        return results

    def tap_selector(self, selector, timeout=15, xml_text=None):
        """
        Wait for the selector (up to timeout) and tap it. Returns True if
        tapped. Pass xml_text to search an already-captured dump first and
        save the extra round trips.
        """
        if xml_text:
            hit = self.find(xml_text, selector)
            if hit:
                self.tap(hit[0], hit[1])
                return True

        hit = self.wait_for(selector, timeout=timeout)
        if not hit:
            return False
        self.tap(hit[0], hit[1])
        return True

    def wait_for(self, selector, timeout=30, interval=3):
        """
        Poll dumps until the selector appears. Each poll is ~2 slow API calls,
        so the effective resolution is coarse — keep timeouts generous.
        Returns (x, y, node) or None on timeout.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            hit = self.find(self.dump_xml(), selector)
            if hit:
                return hit
            time.sleep(interval)
        return None

    def find_or_scroll(self, selector, max_scrolls=5):
        """Look for the selector, scrolling up between attempts."""
        for _ in range(max_scrolls + 1):
            hit = self.find(self.dump_xml(), selector)
            if hit:
                return hit
            self.swipe_up()
        return None

    # ── app / foreground ────────────────────────────────────────────────────
    def open_url(self, url, settle_seconds=4, verify=True):
        """
        Open an Instagram URL inside the Instagram app via a VIEW intent.

        The package is pinned explicitly because without it Android is free to
        route the intent to a browser — which actually happened on a real
        device with a /stories/ link (phase-8 dump 05 captured Chrome in the
        foreground). Opening content by URL DOES work on mobile, unlike the
        "go home" case; there just is no home-equivalent URL.

        Returns True when Instagram holds the foreground afterwards (or, when
        verify=False, immediately after the settle without the extra
        foreground call — used by time-critical flows like stories where the
        interstitial only shows ~3s and every API call costs ~1.6s).
        """
        # Quote the URL and escape & so the shell on the device doesn't
        # split the command; ?igsh=... style params survive this way too.
        quoted = url.replace('"', '').replace('&', '\\&')
        self.command(
            f'am start -a android.intent.action.VIEW -d "{quoted}" {self.INSTAGRAM_PKG}'
        )
        time.sleep(settle_seconds)
        if not verify:
            return True
        return self.foreground_package() == self.INSTAGRAM_PKG

    def in_browser(self):
        """True when a known browser package holds the foreground."""
        return self.foreground_package() in self.BROWSER_PKGS

    def foreground_activity(self):
        """
        'pkg/activity' of the focused window, or '' if it can't be parsed.
        This is the ground truth for "did that tap actually work".
        """
        out = self.command('dumpsys window | grep mCurrentFocus', want_output=True)
        m = re.search(r'[\w.]+/[\w.]+', out or '')
        return m.group(0) if m else (out or '').strip()

    def foreground_package(self):
        fg = self.foreground_activity()
        return fg.split('/')[0] if '/' in fg else fg

    def foreground_activity_name(self):
        """
        Short activity class name (e.g. 'MainTabActivity'), the form the
        login/switch flows compare against. IG activity paths vary between
        builds, but the trailing class name is stable.
        """
        fg = self.foreground_activity()
        if '/' not in fg:
            return fg
        return fg.split('/')[-1].split('.')[-1]

    def is_on_activity(self, activity_name):
        return activity_name in self.foreground_activity()

    # The bottom tab bar is the only reliable proof that Instagram is on a
    # main tab. The activity name is NOT: the Explore/reels viewer runs inside
    # the same MainTabActivity while hiding the tab bar, so checking the
    # activity alone reports "home" from screens where nothing is tappable.
    TAB_BAR_SELECTORS = ({'rid': 'feed_tab'}, {'rid': 'profile_tab'})

    def is_on_home(self, xml_text=None):
        """True when the bottom tab bar is on screen. Costs a dump if not given."""
        xml_text = xml_text or self.dump_xml()
        return any(self.find(xml_text, selector)
                   for selector in self.TAB_BAR_SELECTORS)

    def launcher_component(self):
        """
        The 'package/activity' Android would start for this app, asked of the
        device rather than hardcoded: Instagram's main activity differs between
        builds (InstagramMainActivity on some, MainTabActivity on others), so a
        fixed component name would silently break on an update. Resolved once
        and cached for the life of the worker.
        """
        if self._launcher_component:
            return self._launcher_component

        try:
            out = self.command(
                f'cmd package resolve-activity --brief {self.INSTAGRAM_PKG}',
                want_output=True,
            )
        except Exception as e:
            print(f'[duoplus] could not resolve launcher activity: {e}')
            return None

        for line in reversed((out or '').strip().splitlines()):
            line = line.strip()
            if '/' in line and ' ' not in line:
                self._launcher_component = line
                return line
        return None

    def open_home_intent(self):
        """
        Bring Instagram to its main tab by starting the launcher activity with
        CLEAR_TOP, which drops everything stacked above it.

        This is the middle ground between pressing back (unpredictable — from
        an unknown screen it can lead anywhere) and hard_reset (reliable but a
        ~10s cold start). It costs one call plus a settle, and unlike a
        plain launch it actually resets the stack. There is no URL equivalent:
        instagram.com opens a browser, and the instagram:// deep links all
        target specific content rather than "go home".
        """
        component = self.launcher_component()
        if not component:
            return False

        # 0x14000000 = FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TOP
        self.command(f'am start -n {component} -f 0x14000000')
        time.sleep(3)
        return True

    def go_home(self):
        """
        Get Instagram to a main tab, verified by the tab bar actually being
        present, escalating only as far as needed:

          1. already there            -> one dump, done
          2. CLEAR_TOP launch intent  -> ~3s, clears the activity stack
          3. force-stop and relaunch  -> ~10s, deterministic last resort

        Back presses are deliberately not used: they cost the same as the
        intent but only move one screen and can land anywhere.
        """
        if self.foreground_package() != self.INSTAGRAM_PKG:
            self.start_app()

        if self.is_on_home():
            return True

        if self.open_home_intent() and self.is_on_home():
            return True

        return self.hard_reset()

    def hard_reset(self):
        """
        Force-stop Instagram and relaunch it. Deterministic: it clears whatever
        activity stack the app was stuck in and always reopens on the main
        feed, so it's the recovery path after an error or an unrecognised
        screen. Costs a cold start (~8s), which is why it isn't the first
        thing tried.
        """
        self.command(f'am force-stop {self.INSTAGRAM_PKG}')
        time.sleep(2)
        self.command(
            f'monkey -p {self.INSTAGRAM_PKG} -c android.intent.category.LAUNCHER 1'
        )
        time.sleep(8)
        return self.is_on_home()

    def start_app(self, pkg=None, verify_timeout=25):
        """
        Launch an app and VERIFY it actually came to the foreground. In real
        testing app/start returned OK while the phone was still on the
        launcher, so the OK is never trusted: we poll the foreground and fall
        back to a monkey launch if needed.
        """
        pkg = pkg or self.INSTAGRAM_PKG

        self._post(self.APP_START_PATH, {'image_ids': [self.phone_id], 'pkg': pkg})

        if self._wait_foreground(pkg, verify_timeout):
            return True

        # Fallback: monkey fires the launcher intent directly over shell.
        print(f'[duoplus] app/start did not surface {pkg}, falling back to monkey')
        self.command(f'monkey -p {pkg} -c android.intent.category.LAUNCHER 1')

        if self._wait_foreground(pkg, verify_timeout):
            return True

        raise DeviceCommandError(f'could not bring {pkg} to foreground')

    def _wait_foreground(self, pkg, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if self.foreground_package() == pkg:
                    return True
            except Exception as e:
                print(f'[duoplus] foreground check failed: {e}')
            time.sleep(2)
        return False

    # ── lifecycle ───────────────────────────────────────────────────────────
    def init(self):
        """
        Mirror of BasePlaywright.init(): make sure the device is on and ready.
        No profile/browser setup is needed here — the phone IS the profile.
        """
        self.boot_mobile()
        return self

    def cleanup(self):
        # Intentionally does NOT power the phone off (always-on policy).
        # Kept for symmetry with BasePlaywright.cleanup() in the finally block.
        pass