from script.extra.actions.delete_initial_posts.strategies.InitialPostsDeletedAlready import InitialPostsDeletedAlready
from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.delete_initial_posts.BrowserDeleteInitialPostsEvent import BrowserDeleteInitialPostsEvent
import traceback


class DeleteInitialPostsContext(InstagramMiddleware):
    ig = None
    strategies = [InitialPostsDeletedAlready]

    def execute(self):
        try:
            self.cant_perform()

            BrowserDeleteInitialPostsEvent(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem Deleting initial posts : {str(e)}')
            self.ig.account.add_log(f'Problem Deleting initial posts : {traceback.format_exc()}')

        return False
