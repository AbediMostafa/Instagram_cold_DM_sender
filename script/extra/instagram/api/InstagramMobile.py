from script.extra.instagram.api.InstagramMobileMiddleware import InstagramMobileMiddleware
from script.extra.events.api_events.GetThreadMessagesEvent import GetThreadMessagesEvent


class InstagramMobile(InstagramMobileMiddleware):
    account = None
    session = None
    client = None
    proxy = None
    feeds = None

    def set_proxy(self):

        try:
            self.proxy = self.account.get_proxy()
            self.account.add_cli('Setting proxy')

            if not self.proxy:
                self.account.add_cli('There is no proxy')
                self.account.add_log('There is no proxy')
                raise Exception('There is no proxy')

            before_ip = self.client._send_public_request("https://api.ipify.org/")
            self.account.add_cli(f'Before IP: {before_ip}')

            self.client.set_proxy(
                f"http://{self.proxy.username}:{self.proxy.password}@{self.proxy.ip}:{self.proxy.port}")
            after_ip = self.client._send_public_request("https://api.ipify.org/")

            self.account.add_cli(f'After setting IP: {after_ip}')

            if before_ip == after_ip:
                self.account.add_cli('Before and after ips are same')
                self.account.add_log('Before and after ips are same')
                raise Exception('Before and after ips are same')

            return self

        except Exception as e:
            raise Exception(str(e))

    def log_in(self):
        self.set_proxy()
        session = self.account.get_mobile_session()

        try:
            self.account.add_cli("Trying to use mobile session to login")
            self.client.set_settings(session)
            super().login(
                self.account.username,
                self.account.password,
                verification_code=self.account.get_verification_code()
            )

            try:
                self.account.add_cli("Trying to get feeds")
                self.feeds = self.get_timeline_feed()

            except Exception as e:
                self.account.add_cli(str(e))
                old_session = self.client.get_settings()

                self.client.set_settings({})
                self.client.set_uuids(old_session["uuids"])
                super().login(
                    self.account.username,
                    self.account.password,
                    verification_code=self.account.get_verification_code()
                )

                self.account.add_cli("Trying to get feeds again ... ")
                self.feeds = self.get_timeline_feed()

            self.account.save_mobile_session(self.client.get_settings())

        except Exception as e:
            self.error_handler.handle_exception(f'Problem logging in : {str(e)}')

#
