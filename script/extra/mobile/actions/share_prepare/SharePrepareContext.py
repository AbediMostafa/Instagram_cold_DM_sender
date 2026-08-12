from script.extra.mobile.base.MobileMiddleware import MobileMiddleware
from .SharePrepareEvent import SharePrepareEvent


class SharePrepareContext(MobileMiddleware):
    """
    Share PREPARE module. Its own package (share_prepare) separate from the
    execution module (share), so the two register as distinct modules and can
    be attached to a workflow independently.

    Runs at a higher priority than ShareContext, so within one session
    unprepared orders are claimed/validated before the execution window
    starts eating time.

    Batch-driven, not time-driven: it prepares up to
    mobile_share_prepare_batch orders per session and returns. All the actual
    work — atomic claiming, validation with the web error classification, the
    proving send, and creating every OrderAction upfront — lives in
    SharePrepareEvent.

    No eligibility strategies: whether there is anything to do is decided by
    the claim query itself, and an empty queue costs a single cheap SELECT.
    """

    strategies = []

    def execute(self):
        SharePrepareEvent(self.device).init()
        return True
