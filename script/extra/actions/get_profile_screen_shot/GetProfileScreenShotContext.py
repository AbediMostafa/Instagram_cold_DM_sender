from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.get_profile_screen_shot.BrowserGetProfileScreenShotEvent import BrowserGetProfileScreenShotEvent
from script.extra.actions.get_profile_screen_shot.strategies.AlreadyTookScreenShot import AlreadyTookScreenShot
import traceback


class GetProfileScreenShotContext(InstagramMiddleware):
    ig = None
    strategies = [AlreadyTookScreenShot]

    def execute(self):
        try:
            self.cant_perform()

            BrowserGetProfileScreenShotEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem getting profile screen shot : {str(e)}')
            self.ig.account.add_log(f'Problem getting profile screen shot : {traceback.format_exc()}')

        return False
