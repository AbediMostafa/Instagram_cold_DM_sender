from script.extra.exceptions import CantPerformAction
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from .BrowserLeadGenerateByInstagramSuggestionEvent import BrowserLeadGenerateByInstagramSuggestionEvent


class LeadGenerateByInstagramSuggestionContext(InstagramMiddleware):
    ig = None
    strategies = []

    def execute(self):

        if self.cant_perform():
            return False

        BrowserLeadGenerateByInstagramSuggestionEvent(self.ig).init()

    def cant_perform(self):
        try:
            for strategy in self.strategies:
                strategy(self.ig.account).can()

        except CantPerformAction as e:
            return True

        except Exception as e:
            self.ig.account.add_cli(str(e))

        return False
