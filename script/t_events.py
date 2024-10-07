import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from script.models.Account import Account
# from script.models.Command import Command
from script.models.AccountTemplate import AccountTemplate
from script.models.Template import Template
# from datetime import datetime, timedelta
# from script.extra.process.Process import Process
from script.models.AccountHelper import *
from time import sleep
from script.extra.adapters.SettingAdapter import SettingAdapter
from spintax import spin

from script.extra.instagram.api.InstagramMobile import InstagramMobile
# from script.extra.events.api_events.GetThreadMessagesEvent import GetThreadMessagesEvent
from script.extra.events.api_events.PostVideoEvent import PostVideoEvent
# from script.extra.events.browser_events.BrowserChangeUsernameEvent import BrowserChangeUsernameEvent
# from script.extra.events.browser_events.BrowserChangeNameEvent import BrowserChangeNameEvent
# from script.extra.events.browser_events.BrowserChangeBioEvent import BrowserChangeBioEvent
# from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
# from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
# from script.extra.events.browser_events.BrowserLoomFollowUpEvent import BrowserLoomFollowUpEvent
# from script.extra.events.browser_events.BrowserDeleteInitialPostsEvent import BrowserDeleteInitialPostsEvent
# from script.extra.events.browser_events.BrowserGetThreadMessagesEvent import BrowserGetThreadMessagesEvent
# from script.extra.events.browser_events.BrowserSendDmEvent import BrowserSendDmEvent
# from script.extra.events.browser_events.BrowserPostVideoEvent import BrowserPostVideoEvent
from script.extra.events.browser_events.BrowserPostCarouselEvent import BrowserPostCarouselEvent
# from script.extra.events.api_events.ChangeAvatarEvent import ChangeAvatarEvent
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
from script.extra.events.browser_events.BrowserGoToTargetAccountAndExplorePosts import \
    BrowserGoToTargetAccountAndExplorePosts
from script.extra.events.browser_events.BrowserGotoExploreEvent import BrowserGotoExploreEvent
from script.extra.events.browser_events.BrowserPostImageEvent import BrowserPostImageEvent
from script.extra.events.browser_events.BrowserChangeAvatarEvent import BrowserChangeAvatarEvent
from script.extra.events.browser_events.BasePlaywright import BasePlaywright
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Lead import Lead
from script.models.Thread import Thread
from script.models.Message import Message
from script.models.Command import Command

account = get_next_account()

# ig_mobile = InstagramMobile(account)
# ig_mobile.log_in()
browser_ig = BasePlaywright(account)
BrowserLoginEvent(browser_ig).fire()
# BrowserSendDmEvent(browser_ig).fire()
# BrowserGetThreadMessagesEvent(browser_ig).fire()
browser_ig.pause(1000000, 2000000)

class BrowserLoginEvent(InstagramMiddleware):
    def execute(self):
        self.go_to_instagram()

    def go_to_instagram(self):
        self.ig.account.add_cli('Going to Instagram page ...')
        retries = 3
        for attempt in range(retries):
            try:
                self.ig.page.goto('https://www.instagram.com/', timeout=200000)
                break
            except Exception as e:
                self.ig.account.add_cli(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                sleep(2)

        self.ig.account.add_cli('After Instagram loaded and before timeout')
        self.ig.pause(4000, 6000)
        return self
class BrowserGetThreadMessagesEvent(InstagramMiddleware):
    base = None
    thread = None
    db_message = None
    text = None
    scroll_top_value = None
    users_container = 'div[aria-label="Chats"] .x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1rife3k.x1n2onr6.xh8yej3.x16o0dkt'
    chat_container = 'div.x1uipg7g.xu3j5b3.xol2nv.xlauuyb .x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1rife3k.x1n2onr6.xh8yej3.x16o0dkt'
    text_container = 'div.x1eb86dx div.html-div.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1gslohp.x11i5rnm.x12nagc.x1mh8g0r.x1yc453h.x126k92a.x18lvrbx'
    unread_conversation_selector = 'div[role="listitem"]:has(span.x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x9f619.x3nfvp2.xl56j7k.x1tu34mt.xdk7pt.x1xc55vz.x1emribx)'
    # conversation_selector = 'div[role="button"].x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.x2lwn1j.xeuugli.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1lliihq.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xg6hnt2.x18wri0h.x1l895ks.x1y1aw1k.xwib8y2.xbbxn1n.xxbr6pl'
    conversation_selector = 'div[role="button"].x1i10hfl.x1qjc9v5.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.x2lwn1j.xeuugli.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1lliihq.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1y1aw1k.xwib8y2.xbbxn1n.xxbr6pl:visible'

    def execute(self):
        self.ig.account.add_cli('Getting unread messages ...')

        self.base = BrowserBaseEvent(self.ig)
        self.base.go_to_threads()

        self.ig.account.add_cli("Getting unread conversations")

        self.ig.pause(6000, 8000)
        self.scroll_and_process_unread_conversations(30)

    def scroll_and_process_unread_conversations(self, scroll_times):
        self.ig.account.add_cli(f'Starting to scroll and process unread conversations over {scroll_times} scrolls')

        for _ in range(scroll_times):
            self.get_and_process_unread_conversations()
            self.scroll(self.users_container, 400, 600, 2000, 3000)  # Scroll a single time

    def scroll(self, element, min_length, max_length, min_pause, max_pause):
        scroll_length = random.randint(min_length, max_length)

        self.scroll_top_value = self.ig.page.evaluate('''
            ({selector, scrollLength}) => {
                const element = document.querySelector(selector);
                if (element) {
                    element.scrollBy({
                        top: scrollLength,
                        behavior: 'smooth'
                    });
                    return element.scrollTop; 
                }
                return null;
            }
        ''', {'selector': element, 'scrollLength': scroll_length})

        # Pause for the specified duration
        self.ig.pause(min_pause, max_pause)

    def get_and_process_unread_conversations(self):
        unread_conversations = self.ig.page.locator(self.conversation_selector).all()

        counter = 0

        for conversation in unread_conversations:
            counter += 1
            self.ig.account.add_cli(f'Processing {counter} unread conversation')

            self.click_on_conversation(conversation)
            self.ig.pause(3000, 3800)
            # self.thread = Thread.select().where(Thread.thread_url_id == self.base.get_thread_id()).first()
            #
            # if not self.thread:
            #     self.ig.account.add_cli(f'Thread with url_id {self.base.get_thread_id()} does not exist')
            #     continue

            self.extract_messages()
            sleep(1000)

    def extract_messages(self):
        self.scroll_to_top()

        for _ in range(10):
            self.get_messages()
            self.scroll(self.chat_container, 800, 1000, 1000, 1900)

    def write(self, txt):
        # Open the file in append mode ('a' means it will not overwrite existing content)
        with open("output.txt", "a",  encoding="utf-8") as file:
            file.write(txt + "\n")
            print("Written to the file.")

    def get_messages(self):
        parent_elements = self.ig.page.locator(self.text_container).all()

        for message_parent in parent_elements:
            try:
                self.text = message_parent.inner_html()
            except:
                continue
            self.ig.account.add_cli(f'processing {self.text}')
            self.write(self.text)

            # self.db_message = Message.select().where(
            #     (Message.thread == self.thread) &
            #     (Message.text.contains(self.text))
            # ).first()
            #
            # if not self.db_message:
            #     self.ig.account.add_cli(f'We have new message with the txt of : {self.text}')
            #
            #     self.new_message_process()

            self.ig.pause(2000, 2800)

    def scroll_to_top(self):

        for _ in range(10):
            self.scroll(self.chat_container, -600, -400, 2000, 2900)
            self.ig.account.add_cli(f'scroll top value {self.scroll_top_value}')

            # if self.scroll_top_value < 100:
            #     break

    def new_message_process(self):
        state_mapper = {
            'dm follow up': 'unseen dm reply',
            'unseen dm reply': 'unseen dm reply',
            'seen dm reply': 'unseen dm reply',
            'failed dm': 'unseen dm reply',

            'interested': 'interested',
            'not interested': 'not interested',
            'needs response': 'needs response',

            'loom follow up': 'unseen loom reply',
            'unseen loom reply': 'unseen loom reply',
            'seen loom reply': 'unseen loom reply',
            'failed loom dm': 'unseen loom reply',
            'free': 'free'
        }

        self.thread.lead.change_state(
            account=self.ig.account,
            state=state_mapper[self.thread.lead.last_state],
            update_date=True
        )

        self.db_message = Message.create(
            thread=self.thread,
            text=self.text,
            sender='lead',
            type='text',
            state='unseen',
        )

    def click_on_conversation(self, conversation):
        try:
            conversation.click()
            self.ig.account.add_cli('Conversation clicked')

        except Exception as e:
            self.ig.account.add_cli(f'Problem clicking on unread conversation : {e}')
class BrowserSendDmEvent(InstagramMiddleware):
    dm = None
    command = None
    allowed_leads_count = None
    base = None

    def execute(self):
        self.base = BrowserBaseEvent(self.ig)
        self.base.go_to_threads()
        self.send_dms()

    def send_dms(self):
        self.ig.account.set_state('sending DM', 'app_state')
        lead_ids = [236560, 236561, 236562, 236563, 236564, 236565, 236566, 236567, 236568, 236569, 236570, 236571, 236572, 236573, 236574, 236575]

        for lead_id in lead_ids:
            lead = Lead.get_by_id(lead_id)
            lead.dm_text = spin(SettingAdapter.cold_dm_spintax())

            self.send_dm(lead)
            self.ig.pause(3000, 6000)

    def send_dm(self, lead):

        try:
            self.ig.account.add_cli(f"Sending Dm to : {lead.username}")
            self.send_direct(lead)
            self.ig.account.add_direct_url_id(lead.dm_text, lead, self.base.get_thread_id())

        except Exception as e:
            self.ig.account.add_cli(f"Failed to send DM : {str(e)}")

    def send_direct(self, lead):
        self.ig.page.get_by_role("button", name="New message", exact=True).click(timeout=3000)
        self.ig.pause(3000, 4500)
        self.ig.page.get_by_placeholder("Search...").fill(lead.username)
        self.ig.pause(4000, 6000)

        try:
            self.ig.page.click(f'//text()[contains(., "{lead.username}")]/ancestor::div[@role="button"]', timeout=3000)
        except Exception as e:
            self.ig.page.reload()
            self.ig.pause(4000, 5000)
            self.ig.account.add_cli(f"User does not exists, deleting command ...")
            raise e

        self.ig.pause(3000, 5500)
        self.ig.page.get_by_role("button", name="Chat").click()
        self.ig.pause(3000, 4500)
        self.ig.page.get_by_label("Message", exact=True).fill(lead.dm_text)
        self.ig.pause(4000, 6000)
        self.ig.page.get_by_role("button", name="Send", exact=True).click()
        self.ig.pause(4000, 6000)







# BrowserPostImageEvent(browser_ig).fire()
# BrowserPostCarouselEvent(browser_ig).fire()
# PostVideoEvent(account).fire()


# BrowserGetThreadMessagesEvent(browser_ig).fire()


# BrowserGoToTargetAccountAndExplorePosts(browser_ig, user_type='account', user_numbers=1,
#                                         post_numbers=random.randint(4, 10),
#                                         load_more_comments_number=5, scroll_before_click=True,
#                                         number_of_scrolls=3).fire()
#
# BrowserGoToTargetAccountAndExplorePosts(browser_ig, user_type='random_user', user_numbers=random.randint(2, 5),
#                                         post_numbers=random.randint(4, 10),
#                                         load_more_comments_number=5, scroll_before_click=True,
#                                         number_of_scrolls=5).fire()
#


# BrowserSendDmEvent(browser_ig).fire()
# BrowserGetThreadMessagesEvent(browser_ig).fire()
# # BrowserChangeAvatarEvent(browser_ig).fire()
# BrowserPostCarouselEvent(browser_ig).fire()
# BrowserGotoExploreEvent(browser_ig).fire(),


