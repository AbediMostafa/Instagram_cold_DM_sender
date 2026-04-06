from script.extra.helper import go_to_page
from script.models.Template import get_next
from script.models.LeadBlock import LeadBlock
from script.models.Lead import Lead


class BrowserBlockAssociatedLeadEvent:

    def __init__(self, ig):
        self.ig = ig

        self.lead_block = None
        self.lead = None

        self.ig.account.add_cli('Blocking associated lead ...')
        self.get_lead_block_record()
        self.get_lead()

    def get_lead_block_record(self):
        self.lead_block = LeadBlock.get_or_none(LeadBlock.account == self.ig.account)

        if self.lead_block and self.lead_block.blocked == 1:
            raise Exception("This account's lead has been blocked before ...")

    def get_lead(self):
        self.lead = Lead.select().where(Lead.account == self.ig.account).first()

        if not self.lead:
            raise Exception("There's no lead associated with this account.")

    def init(self):

        self.go_to_lead_page()
        self.block_lead()

    def go_to_lead_page(self):

        self.ig.account.add_cli('Going to lead page')
        go_to_page(self.ig, f"https://www.instagram.com/{self.lead.username}", "Lead")
        self.ig.pause(4000, 5000)

    def block_lead(self):

        self.ig.page.get_by_role("button", name="Options").click(timeout=3000)
        self.ig.pause(2500, 3500)
        self.ig.page.get_by_role("button", name="Block").click(timeout=3000)
        self.ig.pause(2500, 3500)
        self.ig.page.get_by_role("button", name="Block").click(timeout=3000)
        self.ig.pause(2500, 3500)

        lead_block, created = LeadBlock.get_or_create(
            account=self.ig.account,
            blocked=1
        )

        self.ig.account.add_cli("Lead blocked successfully ... ")
