from random import random

from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.models.Lead import Lead
from script.models.Setting import Setting
from script.extra.parsers.LeadGetPkParser import LeadGetPkParser
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.helper import tehran_now

import random
import re
import os


class BrowserGetProfileScreenShotEvent:
    command = None
    number_of_leads = None
    users = None
    lead = None

    def __init__(self, ig):
        self.ig = ig

    def init(self):
        self.ig.account.add_cli(f"Getting Account screen shot ...")
        DirectlyGoToAccountPageAction(self.ig).start(self.ig.account.username)
        self.ig.pause(6000, 7000)
        self.take_screenshot()

    def take_screenshot(self):
        # Create directory structure
        base_dir = os.path.join('../backend', 'storage', 'app', 'public', 'uploads', 'screen_shots')
        os.makedirs(base_dir, exist_ok=True)

        # Create screenshot file name
        screenshot_name = f"{self.ig.account.id}.png"
        screenshot_path = os.path.join(base_dir, screenshot_name)

        # Take the screenshot
        self.ig.page.screenshot(path=screenshot_path)
        self.ig.account.set('screenshot_taken', 1)
        self.ig.account.add_cli(f"Screenshot saved")
