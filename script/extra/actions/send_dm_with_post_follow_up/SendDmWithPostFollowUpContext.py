from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.exceptions import CantPerformAction, IsNotProperServer
import traceback
from .BrowserSendDmWithPostFollowUpEvent import BrowserSendDmWithPostFollowUpEvent


class SendDmWithPostFollowUpContext:
    ig = None
    strategies = []

    def __init__(self, ig, times):
        self.ig = ig

    def execute(self):
        try:
            self.cant_perform()

            BrowserSendDmWithPostFollowUpEvent(self.ig, times).init()

        except CantPerformAction as e:
            return True

        except IsNotProperServer as e:
            self.ig.account.add_cli(str(e))
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem sending DM : {str(e)}')
            self.ig.account.add_log(f'Problem sending DM : {traceback.format_exc()}')

        return False

    def cant_perform(self):
        for strategy in self.strategies:
            strategy(self.ig.account).can()
