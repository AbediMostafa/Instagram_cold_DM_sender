import os
from script.extra.helper import tehran_now


class BaseAction:

    def __init__(self, ig):
        self.ig = ig
        self.account_age = self.ig.account.get_passed_days_since_creation()

    def take_screenshot(self, command_name='like_and_comment', command_id='',
                        fail_or_success='success'):
        # Get current date components
        now = tehran_now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        timestamp = now.strftime("%H%M%S")

        # Create directory structure
        base_dir = os.path.join(
            'screen_shots',
            command_name,
            month,
            day,
            str(command_id),
            fail_or_success)
        os.makedirs(base_dir, exist_ok=True)

        # Create screenshot file name
        screenshot_name = f"{self.ig.account.id}_{command_id}_{timestamp}.png"
        screenshot_path = os.path.join(base_dir, screenshot_name)

        # Take the screenshot
        self.ig.page.screenshot(path=screenshot_path, animations="disabled", omit_background=True)
        self.ig.account.add_cli(f"Screenshot saved")
