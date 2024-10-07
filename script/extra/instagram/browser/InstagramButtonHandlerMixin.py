class InstagramButtonHandlerMixin:

    def allow_cookies(self):
        self.account.add_cli('allowing all cookies ...')
        self.click_by_role("Allow all cookies")
        self.pause(3000, 4000)
        return self

    def save_info(self):
        try:
            self.account.add_cli('Saving information ...')
            self.page.get_by_role("button", name="Save info", exact=True).click(timeout=3500)
            self.pause(5000, 6000)
        except:
            self.account.add_cli("Save info doesn't exists")
            pass

    def turn_on_notif(self):
        self.account.add_cli('Turn on notification')
        self.click_by_role("Turn On")
        self.pause(5000, 6000)

    def continue_as(self):
        if self.is_visible_by_text('Continue as'):
            self.account.add_cli('Continue as is visible, Clicking on it')
            self.click_by_text('Continue as')
            self.pause(3000, 4000)

    def click_and_raise_if_cant(self, message, button_name, err, button_type="link"):
        try:
            self.account.add_cli(message)
            self.page.get_by_role(button_type, name=button_name).click(timeout=5000)
            self.pause(4000, 5000)

        except Exception as e:
            self.handle_exception(f'{err}:{str(e)}')

    # def click_on_profile(self):
    #     button_name = f"{self.account.username}'s profile picture Profile"
    #     self.click_and_raise_if_cant('Going to profile page', button_name, 'Problem clicking on profile selector')

    # def click_on_options(self):
    #     self.click_and_raise_if_cant(
    #         'Clicking on Options button',
    #         'Options',
    #         'Problem clicking on Options',
    #         "button"
    #     )

    # def click_on_facebook_wordmark(self):
    #     button_name = 'Facebook wordmark and family of apps logo Accounts Center Manage your connected experiences and account settings across Meta technologies. Personal details Password and security Ad preferences See more in Accounts Center'
    #     self.click_and_raise_if_cant(
    #         'Clicking on Facebook wordmakr',
    #         button_name,
    #         'Problem clicking on Facebook wordmakr')

    # def click_on_settings_and_privacy(self):
    #     self.click_and_raise_if_cant(
    #         'Clicking on Settings and privacy',
    #         'Settings and privacy',
    #         'Problem clicking on Settings and privacy',
    #         "button"
    #     )

    def click_on_users_instagram(self):
        button_name = f"{self.account.username}\nInstagram"
        self.click_and_raise_if_cant('Going to users Instagram', button_name, 'Problem clicking on users Instagram')

    def click_on_profile_attribute(self, name):
        self.account.add_cli(f"Clicking on {name} to change it")
        self.page.get_by_role("link", name=name, exact=True).click(timeout=5000)
        self.pause(4000, 5000)

    def fill_property(self, label_name, name):
        self.account.add_cli("Filling the name")
        self.page.get_by_label(label_name).fill(name)
        self.pause(2000, 3000)
