class BaseMobileEvent:
    """
    Base for every mobile *Event* - the mobile mirror of the web
    BrowserLoginEvent / BrowserSavePostEvent (BaseAction). An Event holds the
    actual device work; its Context fires it via init() after the eligibility
    strategies pass.

    Like the web events it takes the session handle (`device`, the mobile
    `ig`) and reaches everything through it: device.account for the account,
    device.tap()/dump_xml()/... for the phone.

    Logging: each Event logs its own milestones through self.log(), exactly
    like the browser events log through account.add_cli() - the operational
    trace lives in the Event that owns the flow, not in shared helpers.
    """

    def __init__(self, device):
        self.device = device
        self.account = device.account

    def init(self):
        raise NotImplementedError

    def log(self, msg):
        self.account.add_cli(f'[{self.__class__.__name__}] {msg}')