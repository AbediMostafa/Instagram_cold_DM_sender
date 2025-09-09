from script.models.AccountHelper import get_next_account
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy
from script.extra.base.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
import traceback
from script.extra.actions.login.LoginContext import LoginContext

from script.extra.hooks.RecordLastActivityHook import RecordLastActivityHook
from script.extra.hooks.CheckForLastLoginHook import CheckForLastLoginHook
from script.extra.hooks.CheckForWarningsHook import CheckForWarningsHook
from script.extra.hooks.CheckForAccountActionsHook import CheckForAccountActionsHook
from script.extra.modules.adspower.ProfileUpdator import ProfileUpdator

from time import sleep


class Process:
    account = None
    previous_account = None
    browser_ig = None
    api_ig = None
    should_stop = None

    def get_account(self):
        """
        Sometimes we face Race condition and get_next_account() returns None
        """
        # while not self.account:
        # self.account = get_next_account(specific_ids=[3495])
        self.previous_account = self.account = get_next_account()

    def start(self):
        try:
            self.check_if_previous_browser_is_still_open()
            self.get_account()
            self.should_stop = self.before_process_hooks()

            if self.should_stop:
                return

            self.browser_ig = BasePlaywright(self.account)
            self.browser_ig.init()

            LoginContext(self.browser_ig).fire()
            self.account.set_state('processing', 'app_state')
            self.account.set_state('active')

            self.start_process()

        except Exception as e:
            self.account.add_cli(str(e))
            self.account.add_log(traceback.format_exc())

        finally:
            if self.browser_ig:
                self.browser_ig.cleanup()

            self.account.set_state('idle', 'app_state')

            if not self.should_stop:  # Only record last activity if hooks did not stop the process
                RecordLastActivityHook(self.account)

    def check_if_previous_browser_is_still_open(self):
        print('Checking previous account ... ')
        if self.previous_account:
            creator = ProfileUpdator(self.previous_account)
            creator.call_action('check_account')

    def start_process(self):
        HowManyEventsCanHandleStrategy(self.account, self.browser_ig, self.api_ig).run()

    def before_process_hooks(self):
        account_check = CheckForAccountActionsHook(self.account)

        if account_check.have_custom_messages():
            return False

        # if account_check.cant_start_schedule():
        #     self.account.add_cli('Cant start schedule')
        #     return True

        if CheckForWarningsHook(self.account).last_warning_has_not_expired():
            return True

        if CheckForLastLoginHook(self.account).next_login_not_reached():
            return True

        return False
