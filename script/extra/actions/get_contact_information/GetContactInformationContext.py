from script.extra.actions.get_contact_information.strategies.AlreadyGotContactInformation import \
    AlreadyGotContactInformation
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.get_contact_information.BrowserGetContactInformationEvent import \
    BrowserGetContactInformationEvent
import traceback


class GetContactInformationContext(InstagramMiddleware):
    ig = None
    strategies = [AlreadyGotContactInformation]

    def execute(self):
        try:
            self.cant_perform()

            BrowserGetContactInformationEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem getting contact information : {str(e)}')
            self.ig.account.add_log(f'Problem getting contact information : {traceback.format_exc()}')

        return False
