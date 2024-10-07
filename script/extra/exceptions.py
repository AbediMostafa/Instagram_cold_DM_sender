class ChangePasswordError(Exception):
    pass


class LoginAppearedAgainError(Exception):
    pass


class AccountSuspendedError(Exception):
    pass


class ProblemLogingYouError(Exception):
    pass


class YourPasswordWasIncorrectError(Exception):
    pass


class NotConnectedToTheInternetError(Exception):
    pass


class HelpUsConfirmItsYouError(Exception):
    pass


class MultipleSomethingWentWrongError(Exception):
    pass


class EnterYourEmailError(Exception):
    pass


class AddAPhoneNumberError(Exception):
    pass


class ConfirmYouOwnThisAccount(Exception):
    pass


class FeedbackRequired(Exception):
    pass
