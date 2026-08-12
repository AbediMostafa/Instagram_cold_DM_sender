class BaseMobileModule:
    """
    Base for every type=mobile module — the mobile analogue of the web module
    base. A module is a unit of behaviour a session runs against a device
    (log in, switch account, browse and like, execute an order).

    Contract:
      * The constructor receives the running device (BaseDuoPlus), the target
        account, the service and the mobile. Subclasses override run().
      * run() returns False ONLY to signal "this account is unusable this
        round" (e.g. suspended, login failed) so the session skips it.
        Returning None / True / anything else counts as success.

    Everything goes through the shared BaseDuoPlus instance; modules never
    open their own API connection, so the one-request-per-second budget for
    the device is respected across the whole session.
    """

    def __init__(self, device, account, service=None, mobile=None):
        self.device = device
        self.account = account
        self.service = service
        self.mobile = mobile

    def run(self):
        raise NotImplementedError

    def log(self, msg):
        self.account.add_cli(f'[{self.__class__.__name__}] {msg}')
