import traceback
from .BaseActionState import BaseActionState
from script.extra.actions.Follow import Follow
from script.extra.helper import pause
from script.extra.helper import test_accounts
from script.extra.exceptions import FeedbackRequiredPreferReviewFollower


class FollowEvent(BaseActionState):
    follow = None

    def cant(self):
        return not self.follow.can_follow_today

    def init_state(self):
        self.account.add_cli("Starting follow process")
        self.follow = Follow(self.account)
        self.follow.calculate_today_follows()

    def cant_state(self):
        text = f"We don't have any lead to follow for account : {self.account.username}"
        self.account.add_cli(text)
        self.account.add_log(text)

        return False

    def send_follow_request(self, lead):
        if lead.instagram_id:
            self.account.add_cli(f"Following : {lead.username}")
            self.command = self.account.create_command('follow', 'processing', lead)

            self.ig.follow(lead)
            self.account.add_cli(f"{lead.username} followed successfully")

            # This prevents form changing `dm follow up` state to `followed` state again
            lead.change_state_from_free('followed', self.account)
            self.command.update_cmd('state', 'success')

    def success_state(self):
        self.account.set_state('following', 'app_state')

        for lead in self.follow.leads_to_follow():
        # for lead in test_accounts():

            try:
                self.get_lead_id(lead)
            except Exception as e:
                self.account.add_cli(f"Problem getting lead's id : {str(e)}")
                self.account.add_log(traceback.format_exc())
                lead.delete_instance()
                continue

            pause(3, 5)

            try:
                self.send_follow_request(lead)

            except FeedbackRequiredPreferReviewFollower as e:
                self.command.update_cmd('state', 'fail')
                break

    def exception_state(self, e):
        if self.command:
            self.command.update_cmd('state', 'fail')

        self.account.add_cli(f"Problem following lead: {str(e)}")
        self.account.add_log(traceback.format_exc())
