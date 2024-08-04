import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Account import Account
from script.extra.instagram.InstagramMobile import InstagramMobile


account = Account.get_by_id(37)
ig = InstagramMobile(account)

ig.set_proxy().log_in()


# account = Account.get_by_id(16)

