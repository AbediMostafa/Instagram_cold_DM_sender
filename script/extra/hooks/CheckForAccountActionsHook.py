class CheckForAccountActionsHook:
    account = None

    def __init__(self, account):
        self.account = account
        self.init_possibilities()

    def init_possibilities(self):
        self.account.get_passed_days_since_creation()
        # self.account.calculate_today_dms()
        # self.account.get_number_of_dm_follow_ups()
        # self.account.get_number_of_loom_follow_ups()
        # self.account.get_custom_message_commands()

        self.account.add_cli('------------------------------------------', print_only=True)
        self.account.add_cli(f'Passed days since creation ----------- {self.account.passed_days_since_creation}',
                             print_only=True)
        # self.account.add_cli(f'Total allowed DMS -------------------- {self.account.allowed_number_of_dms}',
        #                      print_only=True)
        # self.account.add_cli(f'Number of DM follow ups -------------- {self.account.allowed_number_of_dm_follow_ups}',
        #                      print_only=True)
        # self.account.add_cli(f'Number of Loom follow ups ------------ {self.account.allowed_number_of_loom_follow_ups}',
        #                      print_only=True)
        # self.account.add_cli(f'Todays sent DMS ---------------------- {self.account.todays_sent_dms}', print_only=True)
        # self.account.add_cli(f'DMs we can send now ------------------ {self.account.current_chunk_dm}', print_only=True)
        #
        # self.account.add_cli(f'Number of custom messages ------------ {self.account.number_of_custom_message_commands}',
        #                      print_only=True)
        self.account.add_cli('------------------------------------------', print_only=True)

    def cant_start_schedule(self):
        should_start_schedule = self.account.final_allowed_number_of_dms > 1 or self.account.can_send_dm_follow_up_today or self.account.can_send_loom_follow_up_today

        return not should_start_schedule

    def have_custom_messages(self):
        we_have_custom_messages = self.account.number_of_custom_message_commands > 0

        if we_have_custom_messages:
            self.account.add_cli(
                f'We have {self.account.number_of_custom_message_commands} custom messages and we start sending now',
                print_only=True)

        return we_have_custom_messages
