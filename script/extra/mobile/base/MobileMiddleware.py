from script.extra.exceptions import CantPerformAction


class MobileMiddleware:
    """
    Base for every mobile *Context* — the mobile mirror of the web
    InstagramMiddleware. A Context is the guarded entry point for one action:
    it runs its eligibility strategies (cant_perform) and, if they pass, fires
    its Event.

    `device` is the mobile analogue of the web `ig`: it carries both the
    DuoPlus primitives and the current session's account (device.account), so
    a Context/Event needs only this one handle, just like the web Context
    needs only `ig`.

    Login/switch is run first and mandatory by SessionRunner (hardcoded, like
    the web LoginContext); the remaining Contexts come from the workflow in
    priority order. A Context doesn't declare when it runs, so there's nothing
    to keep in sync here.

    Subclasses set `strategies` to a list of strategy classes and implement
    execute(). Each strategy is constructed with the device and must raise
    CantPerformAction when the action isn't allowed right now.
    """

    strategies = []

    def __init__(self, device):
        self.device = device
        self.account = device.account

    def cant_perform(self):
        """
        Run every strategy. A strategy signals "not allowed" by raising
        CantPerformAction, which the Context's execute() catches. This is the
        same contract the web strategies use (e.g. CanFollowToday).
        """
        for strategy_cls in self.strategies:
            strategy_cls(self.device).check()

    def execute(self):
        raise NotImplementedError

    def log(self, msg):
        self.account.add_cli(f'[{self.__class__.__name__}] {msg}')