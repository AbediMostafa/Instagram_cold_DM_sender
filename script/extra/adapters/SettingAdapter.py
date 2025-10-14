from script.models.Setting import Setting
from script.models.Spintax import Spintax


class SettingAdapter:

    @classmethod
    def max_account_for_one_proxy(cls):
        return Setting.get_value('Max Account For One Proxy', 10)

    @classmethod
    def max_dm(cls):
        return Setting.get_value('Max DM', 28)

    @classmethod
    def dm_chunk(cls):
        return Setting.get_value('DM Chunk', 9)

    @classmethod
    def max_follow(cls):
        return Setting.get_value('Max Follow', 20)

    @classmethod
    def max_like(cls):
        return Setting.get_value('Max Like', 20)

    @classmethod
    def max_comment(cls):
        return Setting.get_value('Max Comment', 50)

    @classmethod
    def max_get_threads(cls):
        return Setting.get_value('Max Get Threads', 2)

    @classmethod
    def follow_chunk(cls):
        return Setting.get_value('Follow Chunk', 5)

    @classmethod
    def like_chunk(cls):
        return Setting.get_value('Like Chunk', 3)

    @classmethod
    def comment_chunk(cls):
        return Setting.get_value('Comment Chunk', 3)

    @classmethod
    def dm_follow_up_chunk(cls):
        return Setting.get_value('DM Follow Up Chunk', 5)

    @classmethod
    def cold_dm_spintax(cls, account=None):
        return Spintax.get_value(0, account.category if account else None)

    @classmethod
    def first_dm_follow_up_spintax(cls, account=None):
        return Spintax.get_value(1, account.category if account else None)

    @classmethod
    def second_dm_follow_up_spintax(cls, account=None):
        return Spintax.get_value(2, account.category if account else None)

    @classmethod
    def third_dm_follow_up_spintax(cls, account=None):
        return Spintax.get_value(3, account.category if account else None)

    @classmethod
    def minimum_time_for_next_login(cls):
        return Setting.get_value('Minimum time for next login', 3)

    @classmethod
    def maximum_time_for_next_login(cls):
        return Setting.get_value('Maximum time for next login', 5)
