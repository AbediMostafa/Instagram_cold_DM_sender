from script.extra.helper import pause


class BaseActionState:
    ig = None
    account = None
    template = None
    command = None
    avatar_path = None

    def __init__(self, account, ig):
        self.account = account
        self.ig = ig

    def fire(self):
        self.init_state()

        if self.cant():
            return self.cant_state()

        try:
            self.success_state()

        except Exception as e:
            self.exception_state(e)
            raise e

    def get_lead_id(self, lead):
        if not lead.instagram_id:
            self.account.add_cli("Getting lead's instagram_id")
            self.ig.user_id_from_username(lead)
            self.account.add_cli(f"{lead.username}'s instagram_id : {lead.instagram_id}")
            pause(3, 5)
