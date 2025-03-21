from script.extra.actions.make_account_public.strategies.AccountIsOldEnough import AccountIsOldEnough
from script.extra.actions.make_account_public.strategies.AccountIsPublicAlready import AccountIsPublicAlready
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.make_account_public.BrowserMakeAccountPublicEvent import BrowserMakeAccountPublicEvent
import traceback


class MakeAccountPublicContext(InstagramMiddleware):
    ig = None
    strategies = [AccountIsOldEnough, AccountIsPublicAlready]

    def execute(self):
        try:
            self.cant_perform()

            BrowserMakeAccountPublicEvent(self.ig).init()

        except Exception as e:
            self.ig.account.add_cli(f'Problem making account public : {str(e)}')
            self.ig.account.add_log(f'Problem making account public : {traceback.format_exc()}')

        return False
