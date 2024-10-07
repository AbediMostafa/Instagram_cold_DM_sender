class RequestAdapter:

    @classmethod
    def bulkacc_api(cls, secret):
        return f'https://bulkacc.com/TwoFactorEnable/Get2FACode?secretKey={secret}'
