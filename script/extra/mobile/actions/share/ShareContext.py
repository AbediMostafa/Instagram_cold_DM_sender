from script.extra.mobile.base.MobileMiddleware import MobileMiddleware
from .ShareEvent import ShareEvent


class ShareContext(MobileMiddleware):
    """
    Share execution module (lower priority than SharePrepareContext).

    Time-driven: ShareEvent claims free actions from prepared
    (is_prepared=2) orders and fires sends back to back until the
    mobile_share_seconds window (default 300s) runs out, then returns so
    SessionRunner can move on to the rest of the workflow.

    No eligibility strategies: an account with nothing to send exits after
    one cheap claim query.
    """

    strategies = []

    def execute(self):
        ShareEvent(self.device).init()
        return True
