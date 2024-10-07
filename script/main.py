import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Account import Account
from script.extra.instagram.api.InstagramMobile import InstagramMobile
from script.extra.events.api_events.PostVideoEvent import PostVideoEvent
from script.models.AccountHelper import *
from script.models.Message import Message

text = '''
👋 Hey there!

Had your page show up on my feed and I was very impressed by your products. Wanted to reach out personally because I think you've got amazing potential to scale huge on TikTok. 🤩

Right now in 2024 there's a tremendous opportunity on there with UGC. It's the world's best source of low cost, high quality, and high converting traffic. I've helped brands like yours boost their sales by 20k, 30k, even 50k in just 30 days through TikTok UGC—making it *unfairly easy* to do that 😋

I filmed a personalized loom going over your store and why I think you guys in particular would do so well on TikTok.

Would you like me to send it your way?

Cheers, 
E
'''
m = Message.select().where(
    (Message.thread_id == 214073) &
    (Message.text==text)
).first()

print(m)

# account = Account.get_by_id(37)  Edward_TikT0k_Ads0lut0ns
# account = get_next_account()
# PostVideoEvent(account).fire()
# ads.edward_master
# account = Account.get_by_id(51)  ed_digital_wiz
# account = Account.get_by_id(52) ecom_growth_edward
# account = Account.get_by_id(56) ads.master.ed
# ig = InstagramMobile(account)
#
# ig.set_proxy().log_in()


# account = Account.get_by_id(16)
