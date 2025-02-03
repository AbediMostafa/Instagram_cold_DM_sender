from script.extra.playwright.base_actions.BaseAction import BaseAction


class ErrorIndicators(BaseAction):

    def page_is_not_visible_handler(self):
        if self.ig.is_visible_by_text("this page isn't available") or self.ig.is_visible_by_text(
                "The link you followed may be broken, or the page may have been removed"):
            raise Exception("Sorry, this page isn't available")

    def something_went_wrong_handler(self):
        for _ in range(7):
            if self.ig.is_visible_by_text("Something went wrong. Please try again"):
                raise Exception("Something went wrong")

            self.ig.pause(700, 800)

    def not_every_one_can_message_this_account_handler(self, lead):
        if self.ig.is_visible_by_text("Not everyone can message this account"):

            lead.change_state(self.ig.account, 'failed dm', add_history=True, update_date=True)
            raise Exception("Not everyone can message this account")

    def send_more_messages_after_invite_accepted(self):
        if self.ig.is_visible_by_text(
                "You can send more messages after your invite is accepted") or self.ig.is_visible_by_text(
                "You can send more messages after they accept"):

            raise Exception("You can send more messages after your invite is accepted")
