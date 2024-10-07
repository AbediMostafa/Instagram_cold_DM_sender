import sys
import os
from spintax import spin

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Color import get_next_color
from script.models.Account import Account
from script.models.AccountHelper import get_next_account
from script.models.AccountTemplate import AccountTemplate
from script.models.Template import Template
from script.extra.helper import *
from script.models.Template import get_a, delete
from script.models.Spintax import Spintax

account = Account.get_by_id(7)
spintax = Spintax.get_value('cold dm', account.category)






print(spintax)
