from script.models.Command import performed_command_count
from script.models.Lead import Lead
from script.extra.helper import calculate_daily_dms, get_dm_chunk
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
import traceback


class BrowserFollowEvent:
    command = None
    account_age = None

    def __init__(self, ig):
        self.ig = ig
        self.category_model = self.ig.account.category
        self.account_age = self.ig.account.get_passed_days_since_creation()

    def init(self):
        self.ig.account.add_cli('Starting follow leads ...')
        self.perform_follow()

        # leads = Lead.get_leads_for_follow(self.get_allowed_dms())
        #
        # for lead in leads:
        #     self.ig.account.add_cli(f'Following {lead.username} ...')
        #     self.perform_follow(lead)
        #     self.ig.pause(3000, 4000)

    def get_allowed_dms(self):
        performed_follows = performed_command_count(
            self.ig.account,
            ['follow'],
            24)

        allowed_follows = calculate_daily_dms(self.account_age)
        allowed_chunk = get_dm_chunk(self.account_age)
        remained_follows = 0 if performed_follows >= allowed_follows else allowed_follows - performed_follows
        final_allowed_chunk = min(allowed_chunk, remained_follows)

        self.ig.account.add_cli(f'Performed follows                : {performed_follows}')
        self.ig.account.add_cli(f'Allowed follows for this account : {allowed_follows}')
        self.ig.account.add_cli(f'Follow chunk                     : {allowed_chunk}')
        self.ig.account.add_cli(f'Final number                     : {final_allowed_chunk}')

        return final_allowed_chunk

    def perform_follow(self):
    # def perform_follow(self, lead):

        try:
            DirectlyGoToAccountPageAction(self.ig).start('tibtaniem')
            self.ig.pause(3000, 4000)

            self.ig.page.get_by_role("button", name="Follow").first.click()
            self.ig.pause(3000, 4000)

        except Exception as e:
            self.ig.account.add_cli(f'Problem Following lead : {str(e)}')
            self.ig.account.add_log(f'Problem Following lead : {traceback.format_exc()}')

            if self.command:
                self.command.update_cmd('state', 'fail')
