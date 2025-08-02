import random
import math

from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.models.Thread import Thread
from script.models.Message import Message
from datetime import datetime, timezone


class BrowserGetThreadMessagesEvent(InstagramMiddleware):
    base = None
    thread = None
    db_message = None
    text = None
    scroll_top_value = None
    min_chat_box_scroll_top = -800
    max_chat_box_scroll_top = -700

    min_chat_box_scroll_down = 300
    max_chat_box_scroll_down = 400

    users_container = 'div[aria-label="Chats"] .x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1n2onr6.xh8yej3.x16o0dkt'
    chat_container = 'div.x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.xc8icb0.x6ikm8r.x10wlt62.x1ja2u2z  div.x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1odjw0f.x1n2onr6.xh8yej3.x16o0dkt'
    text_container = 'div.x1eb86dx div.html-div.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1gslohp.x14z9mp.x12nagc.x1lziwak.x1yc453h.x126k92a.x18lvrbx'
    unread_conversation_selector = 'div[role="button"]:has(span.x6s0dn4.x1iwo8zk.x1033uif.x179ill4.x1b60jn0.x9f619.x3nfvp2.xl56j7k.x1tu34mt.xdk7pt.x1xc55vz)'
    read_conversation_selector = 'div.x13dflua.x19991ni>div[role="button"].x1i10hfl.x1qjc9v5.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk'

    def execute(self):
        self.ig.account.add_cli('Getting unread messages ...')

        if self.ig.is_visible_by_text('No messages found.'):
            self.ig.account.add_cli('No messages found.')
            return True

        if not self.we_are_in_threads_page():
            self.base.go_to_threads()

        self.ig.turn_on_notif()
        self.scroll_and_process_unread_conversations(random.randint(16, 18))

    def we_are_in_threads_page(self):
        return self.ig.page.url.rstrip("/") == "https://www.instagram.com/direct/inbox"

    def scroll_and_process_unread_conversations(self, scroll_times):
        self.ig.account.add_cli(f'Starting to scroll and process unread conversations over {scroll_times} scrolls')

        for _ in range(scroll_times):
            self.get_and_process_unread_conversations()
            self.scroll(self.users_container, 400, 600, 2000, 3000)  # Scroll a single time

    def scroll(self, element, min_length, max_length, min_pause, max_pause):
        scroll_length = random.randint(min_length, max_length)

        self.ig.page.evaluate('''
            ({selector, scrollLength}) => {
                const element = document.querySelector(selector);
                if (element) {
                    element.scrollBy({
                        top: scrollLength,
                        behavior: 'smooth'
                    });
                }
            }
        ''', {'selector': element, 'scrollLength': scroll_length})

        # Pause for the specified duration
        self.ig.pause(min_pause, max_pause)

    def get_scroll_top(self, element):

        self.scroll_top_value = self.ig.page.evaluate('''
            selector => {
                const element = document.querySelector(selector);
                if (element) {
                    return element.scrollTop; 
                }
                throw new Error("Element not found: " + selector);
            }
        ''', element)

    def get_and_process_unread_conversations(self):
        unread_conversations = self.ig.page.locator(self.unread_conversation_selector).all()

        counter = 0

        for conversation in unread_conversations:
            counter += 1
            self.ig.account.add_cli(f'Processing {counter} unread conversation')

            try:
                conversation.click(timeout=3000)
                self.ig.account.add_cli('Conversation clicked')

            except Exception as e:
                self.ig.account.add_cli(f'Problem clicking on unread conversation : {e}')
                continue

            self.ig.pause(3000, 3800)
            self.thread = Thread.select().where(Thread.thread_url_id == self.base.get_thread_id()).first()

            if not self.thread:
                self.ig.account.add_cli(f'Thread with url_id {self.base.get_thread_id()} does not exist')
                continue

            self.extract_messages()

    def get_number_of_scrolls(self, scroll_height):
        number_of_scrolls = self.scroll_top_value / scroll_height
        return math.ceil(abs(number_of_scrolls))

    def extract_messages(self):
        self.get_scroll_top(self.chat_container)

        self.scroll_to_top()

        number_of_scrolls = self.get_number_of_scrolls(self.min_chat_box_scroll_down)
        self.ig.account.add_cli(f'Number of scrolls down: {number_of_scrolls}')

        for _ in range(number_of_scrolls):
            self.ig.account.add_cli(f'Scrolling down for {_} time')
            self.get_messages()
            self.scroll(
                self.chat_container,
                self.min_chat_box_scroll_down,
                self.max_chat_box_scroll_down, 3000, 3900)

    def get_messages(self):
        parent_elements = self.ig.page.locator(self.text_container).all()

        for message_parent in parent_elements:
            try:
                self.text = message_parent.inner_html(timeout=4000)
            except Exception as e:
                self.ig.account.add_cli(f'Problem getting text of message : {str(e)}')
                continue

            self.db_message = Message.select().where(
                (Message.thread == self.thread) &
                (Message.text == self.text)
            ).first()

            if not self.db_message:
                self.ig.account.add_cli(f'We have new message with the txt of : {self.text}')

                self.new_message_process()

            self.ig.pause(800, 1100)

    def scroll_to_top(self):

        self.ig.account.add_cli(f'Scroll top value : {self.scroll_top_value}')
        number_of_scrolls = self.get_number_of_scrolls(self.max_chat_box_scroll_top)
        self.ig.account.add_cli(f'Number of scrolls up: {number_of_scrolls}')

        for _ in range(number_of_scrolls):
            self.scroll(self.chat_container, self.min_chat_box_scroll_top, self.max_chat_box_scroll_top, 2000, 2900)
            self.ig.account.add_cli(f'scroll top value {self.scroll_top_value}')

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
            'free': 'free',
            'call booked': 'call booked'
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
