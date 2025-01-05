from datetime import datetime, timedelta


class SendDmStrategy:
    ig = None

    def __init__(self, ig):
        self.ig = ig
        pass

    def get_number_of_dms(self):
        if self.ig.account.has_enough_posts:
            return self.ig.account.current_chunk_dm

    def sent_recent_dm_command_within(self, hours=20):
        from script.models.Command import Command

        """
        Check if any successful DM command was sent within the last `hours`.
        """
        time_threshold = datetime.now() - timedelta(hours=hours)

        return (Command
                .select()
                .where(
            (Command.account == self) &
            (Command.type.in_(['dm follow up'])) &
            (Command.times == 0) &
            (Command.state == 'success') &
            (Command.created_at >= time_threshold)
        )
                .exists())
