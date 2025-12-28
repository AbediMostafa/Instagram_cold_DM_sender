from script.models.Setting import Setting
from script.extra.base.MultiloginHandler import MultiloginHandler
from script.extra.base.AdsPowerHandler import AdsPowerHandler


class BrowserHandlerFactory:
    @staticmethod
    def create_handler(account):
        anti_detect_browser = Setting.get_value('anti_detect_browser', 'multilogin')
        if anti_detect_browser == 'multilogin':
            return MultiloginHandler(account)

        elif anti_detect_browser == 'adspower':
            return AdsPowerHandler(account)

        else:
            raise ValueError("Invalid anti_detect_browser setting.")
