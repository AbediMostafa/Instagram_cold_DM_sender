import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Account import Account
from script.extra.instagram.InstagramMobile import InstagramMobile


# account = Account.get_by_id(37)  Edward_TikT0k_Ads0lut0ns
account = Account.get_by_id(47)
# ads.edward_master
# account = Account.get_by_id(51)  ed_digital_wiz
# account = Account.get_by_id(52) ecom_growth_edward
# account = Account.get_by_id(56) ads.master.ed
ig = InstagramMobile(account)

ig.set_proxy().log_in()


# account = Account.get_by_id(16)

