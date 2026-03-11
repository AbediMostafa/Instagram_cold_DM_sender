from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BaseOrderPreparer import BaseOrderPreparer
import traceback


class OrderPreparerContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):
        try:
            self.cant_perform()

            BaseOrderPreparer(self.ig).init()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(f'Problem preparing order: {str(e)}')
            self.ig.account.add_log(f'Problem preparing order: {traceback.format_exc()}')

        return False
