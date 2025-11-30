from script.extra.exceptions import *
import os
import traceback
from datetime import datetime
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.helper import tehran_now


class InstagramMiddleware:
    ig = None

    def __init__(self, ig):
        self.ig = ig
        self.base = BrowserBaseEvent(ig)

    def fire(self):
        try:
            return self.execute()

        except (LoginAppearedAgainError, NotConnectedToTheInternetError) as e:
            self.handle_exception(str(e))

        except (ProblemLogingYouError, YourPasswordWasIncorrectError, MultipleSomethingWentWrongError,
                EnterYourEmailError, AddAPhoneNumberError, FeedbackRequired, EnterYourMobileError,
                HelpUsConfirmItsYouError, SomethingWentWrong, AppealSubmittedError, UploadYourIdError,
                CheckYourTextMessages, FillCodeSentToError, ChangePasswordError) as e:
            self.ig.account.set_state('challenging')
            self.ig.account.add_warning(e, 500)
            self.handle_exception(str(e))

        except (AccountSuspendedError, ConfirmYouOwnThisAccount, AccountDisabledError, CheckTheSecurityCode) as e:
            self.ig.account.set_state('suspended')
            self.ig.account.add_warning(e, 500)
            self.handle_exception(str(e))

        except Exception as e:
            exception_type = type(e)
            exception_class = e.__class__.__name__
            print(f"Exception type: {exception_type}")
            print(f"Exception class: {exception_class}")
            print(str(e))
            self.handle_exception(str(e))

    def take_screenshot(self, cause='something'):
        # Get current date components
        now = tehran_now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        timestamp = now.strftime("%H%M%S")

        # Create directory structure
        base_dir = os.path.join('screen_shots', year, month, day)
        os.makedirs(base_dir, exist_ok=True)

        # Create screenshot file name
        screenshot_name = f"{self.ig.account.id}_{timestamp}.png"
        screenshot_path = os.path.join(base_dir, screenshot_name)

        # Take the screenshot
        self.ig.page.screenshot(path=screenshot_path)
        self.ig.account.add_screen_shot(cause=cause, path=screenshot_path)
        self.ig.account.add_cli(f"Screenshot saved")

    def handle_exception(self, reason, _type='raise'):
        self.ig.account.add_cli(reason)
        self.ig.account.add_log(traceback.format_exc())

        if _type == 'raise':
            raise Exception(reason)

    def cant_perform(self):
        for strategy in self.strategies:
            strategy(self.ig.account).can()
