class InstagramSuspensionHandlerMixin:

    def after_login_error(self, suspension_type, text, full_text):
        if self.is_visible_by_text(text):
            self.account.set_state(state=suspension_type, log=full_text)
            raise Exception(full_text)

    def password_is_incorrect_handler(self):
        self.after_login_error('suspended', 'your password was incorrect', 'Your password was incorrect')
        return self

    def problem_logging_in_handler(self):
        self.after_login_error('suspended', 'was a problem logging you into Instagram',
                               'There was a problem logging you into Instagram .please try again soon')
        return self

    def unusual_login_attempt_handler(self):
        self.after_login_error('challenging', 'We Detected An Unusual Login Attempt',
                               'We Detected An Unusual Login Attempt')
        return self

    def help_us_confirm_its_you_handler(self):
        self.after_login_error('challenging', 'Help us confirm it',
                               "Help us confirm it's you")
        return self

    def suspended_account_handler(self):
        self.after_login_error('suspended', 'We suspended your account',
                               'We suspended your account')
        return self

    def suspect_automate_behavior_handler(self):

        if self.is_visible_by_text('suspect automated behavior'):

            try:
                self.account.add_cli('We suspect automated behavior on your account')
                self.page.get_by_role("button", name='Dismiss').click(timeout=5000)

            except Exception as e:
                self.handle_exception(f'Problem clicking on Dismiss:{str(e)}')
