from script.models.Setting import Setting


class SettingAdapter:

    @classmethod
    def max_account_for_one_proxy(cls):
        return Setting.get_value('Max Account For One Proxy', 4)

    @classmethod
    def max_dm(cls):
        return Setting.get_value('Max DM', 50)

    @classmethod
    def dm_chunk(cls):
        return Setting.get_value('DM Chunk', 3)

    @classmethod
    def max_follow(cls):
        return Setting.get_value('Max Follow', 50)

    @classmethod
    def follow_chunk(cls):
        return Setting.get_value('Follow Chunk', 5)

    @classmethod
    def dm_follow_up_chunk(cls):
        return Setting.get_value('DM Follow Up Chunk', 5)

    @classmethod
    def cold_dm_spintax(cls):
        return Setting.get_value('cold dm spintax')

    @classmethod
    def first_dm_follow_up_spintax(cls):
        return Setting.get_value('first dm follow up spintax')

    @classmethod
    def second_dm_follow_up_spintax(cls):
        return Setting.get_value('second dm follow up spintax')

    @classmethod
    def third_dm_follow_up_spintax(cls):
        return Setting.get_value('third dm follow up spintax')
