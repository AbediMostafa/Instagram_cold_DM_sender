from script.extra.mobile.base.MobileMiddleware import MobileMiddleware
from .ExploreAndLikeEvent import ExploreAndLikeEvent


class ExploreAndLikeContext(MobileMiddleware):
    """
    Warm-up module: browse Explore and like ~20% of the posts it opens, then
    finish. A 'normal' module — SessionRunner runs it once to completion during
    the session (in shuffled order with the other normal modules).

    No eligibility strategy: the like rate itself keeps it human-ish, so
    there's nothing to gate. The strategies hook on MobileMiddleware stays
    available if a cap is ever wanted later.
    """

    strategies = []

    def execute(self):
        ExploreAndLikeEvent(self.device).init()
        return True