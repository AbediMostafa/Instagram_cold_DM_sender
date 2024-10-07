import random

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
    users_container = 'div[aria-label="Chats"] .x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1rife3k.x1n2onr6.xh8yej3.x16o0dkt'
    chat_container = 'div.x1uipg7g.xu3j5b3.xol2nv.xlauuyb .x78zum5.xdt5ytf.x1iyjqo2.xs83m0k.x1xzczws.x6ikm8r.x1rife3k.x1n2onr6.xh8yej3.x16o0dkt'
    text_container = 'div.x1eb86dx div.html-div.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1gslohp.x11i5rnm.x12nagc.x1mh8g0r.x1yc453h.x126k92a.x18lvrbx'
    unread_conversation_selector = 'div[role="listitem"]:has(span.x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x9f619.x3nfvp2.xl56j7k.x1tu34mt.xdk7pt.x1xc55vz.x1emribx)'

    def execute(self):
        self.ig.account.add_cli('Getting unread messages ...')

        self.base = BrowserBaseEvent(self.ig)
        self.base.go_to_threads()
        self.scroll_and_process_unread_conversations(20)

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

    def extract_messages(self):
        self.scroll_to_top()

        for _ in range(10):
            self.get_messages()
            self.scroll(self.chat_container, 300, 400, 1000, 1900)

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
                # (Message.text.contains(self.text))
            ).first()

            if not self.db_message:
                self.ig.account.add_cli(f'We have new message with the txt of : {self.text}')

                self.new_message_process()

            self.ig.pause(800, 1100)

    def scroll_to_top(self):

        for _ in range(13):
            self.scroll(self.chat_container, -600, -400, 2000, 2900)
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
