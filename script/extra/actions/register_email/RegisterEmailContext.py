from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.actions.register_email.BrowserRegisterEmailEvent import BrowserRegisterEmailEvent


class RegisterEmailContext(InstagramMiddleware):
    """
    Context class for handling email registration process
    """

    def execute(self):
        """
        Main execution method that orchestrates the email registration process
        """
        try:
            # Check if Account already verified
            if self.ig.account.is_verify:
                return self.ig.account.add_cli(f"Account already verified")


            # Initialize and execute the email registration event
            email_event = BrowserRegisterEmailEvent(self.ig)
            email_event.init()

        except Exception as e:
            self.ig.account.add_cli(f"Error in email registration context: {str(e)}")
            raise