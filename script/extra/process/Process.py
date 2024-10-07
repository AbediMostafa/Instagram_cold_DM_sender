from script.extra.instagram.api.InstagramMobile import InstagramMobile
from script.models.AccountHelper import *
from script.extra.strategies.HowManyEventsCanHandleStrategy import HowManyEventsCanHandleStrategy
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent

from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
from script.extra.hooks.RecordLastActivityHook import RecordLastActivityHook
from script.extra.hooks.CheckForLastLoginHook import CheckForLastLoginHook
from script.extra.hooks.CheckForWarningsHook import CheckForWarningsHook
from time import sleep


class Process:
    account = None
    browser_ig = None
    api_ig = None

    def start(self):
        try:
            self.account = get_next_account()
            self.account.get_proxy()

            should_stop = self.before_process_hooks()

            if should_stop:
                return  # Exit

            self.browser_ig = BasePlaywright(self.account)
            BrowserLoginEvent(self.browser_ig).fire()
            self.account.set_state('processing', 'app_state')
            self.account.set_state('active')

            self.do_process()

        except Exception as e:
            self.account.add_cli(str(e))
            pass

        finally:
            self.account.set_state('idle', 'app_state')

            if self.browser_ig:
                self.browser_ig.cleanup()

            if not should_stop:  # Only record last activity if hooks did not stop the process
                RecordLastActivityHook(self.account)

    def do_process(self):
        HowManyEventsCanHandleStrategy(self.account, self.browser_ig, self.api_ig).run()

    def before_process_hooks(self):
        if CheckForWarningsHook(self.account).last_warning_has_not_expired():
            return True

        if CheckForLastLoginHook(self.account).next_login_not_reached():
            return True

        return False
