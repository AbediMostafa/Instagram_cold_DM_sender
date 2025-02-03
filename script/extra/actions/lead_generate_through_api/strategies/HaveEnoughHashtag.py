import random
from script.models.Command import performed_command_count
from script.models.Hashtag import get_hashtag
from script.extra.exceptions import DontHaveEnoughEntity


class HaveEnoughHashtag:
    hashtag_count = 3

    def __init__(self, account):
        self.account = account

    def can(self):
        hashtags = get_hashtag(3)

        if hashtags.count() == 0:
            text = f'We dont have enough hashtags, please add more'
            self.account.add_cli(text)
            self.account.add_log(text)
            raise DontHaveEnoughEntity(text)
