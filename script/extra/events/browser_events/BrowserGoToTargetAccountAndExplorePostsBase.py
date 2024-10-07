from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.models.Lead import Lead
from script.models.Account import Account
from peewee import *

import random


class BrowserGoToTargetAccountAndExplorePostsBase(InstagramMiddleware):
    user = None
    username = None
    user_numbers = 1
    post_numbers = 1
    load_more_comments_number = 1
    number_of_scrolls = 1
    scroll_before_click = True
    get_a_user_method = None
    user_list = ['johnlegend', 'johnnydepp', 'therock', 'samirselhaddad', 'samia_suluhu_hassan', 'philfoden',
                 'philadelphiaflyers', 'philippplein', 'drphil', 'arianagrande', 'arianevanessa4', 'arian.heidarii',
                 'arsenal', 'now.afc', 'arsenal_memes___', 'arsenalwfc', 'arsenalnewschannel', 'perspolis',
                 'perspoliss_fc', 'arteshsoooorkh', 'telesena', 'senators', 'senatorvance', 'monbleu', 'sophiabergholm'
                 'relaxinoffgrid','gill.meller','lakeparkbistro','pastagrannies', 'shebakesourdough', 'matt_swack'
                 'heythereney','alessia', 'byrubyfoods'
                 ]

    def execute(self):
        self.base.go_to_home()

        for _ in range(self.user_numbers):
            try:
                self.click_on_search()
                self.get_a_user_method()
                self.go_to_user_page()

                if self.ig.is_visible_by_text('No posts yet'):
                    continue

                if self.scroll_before_click:
                    self.base.scroll(times=self.number_of_scrolls, length=random.randint(450, 650))

                self.click_on_first_post()
                self.go_to_next_posts()
                self.close_post_page()
                self.ig.pause(2000, 4000)

            except Exception as e:
                print(str(e))
                pass

    def click_on_search(self):
        try:
            self.ig.page.get_by_role("link", name="Search Search").click()
            self.ig.account.add_cli('search clicked')
        except:
            self.ig.account.add_cli('Search SEarch doesnt existss')
            self.ig.page.locator(
                'span[aria-describedby=":ri:"] x9f619.x3nfvp2.xr9ek0c.xjpr12u.xo237n4.x6pnmvc.x7nr27j.x12dmmrz.xz9dl7a.xn6708d.xsag5q8.x1ye3gou.x80pfx3.x159b3zp.x1dn74xm.xif99yt.x172qv1o.x10djquj.x1lhsz42.xzauu7c.xdoji71').click(
                timeout=3000)

        self.ig.pause(2000, 3000)

    def get_a_random_lead(self):
        self.user = (Lead.select()
                     .where(Lead.account == self.ig.account)
                     .order_by(fn.Rand())
                     .first())

        if not self.user:
            self.user = (Lead.select()
                         .order_by(fn.Rand())
                         .first())

        self.ig.account.add_cli(f'Selected Lead to explore : {self.user.username}')
        self.username = self.user.username

    def get_a_random_account(self):
        self.user = (Account.select()
                     .order_by(fn.Rand())
                     .first())

        self.ig.account.add_cli(f'Selected Account to explore : {self.user.username}')
        self.username = self.user.username

    def get_a_random_user(self):
        self.username = random.choice(self.user_list)

    def go_to_user_page(self):
        self.ig.page.get_by_placeholder("Search").fill(self.username)
        self.ig.pause(4000, 5000)
        self.ig.page.goto(f'https://www.instagram.com/{self.username}/')

        if self.ig.is_visible_by_text("Sorry, this page isn't available"):
            self.ig.account.add_cli("Current account's page doesnt exists ")
            raise Exception("Current account's page doesnt exists ")

        self.ig.pause(4000, 5000)

    def click_on_first_post(self):
        elem = 'div.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p.xfllauq.xo2y696.x11i5rnm.x2pgyrj a'
        elem_1 = 'div.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p.xfllauq a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr'

        try:
            # Click the first matching element for elem
            self.ig.page.locator(elem).nth(0).click()
            self.load_more_comments()
        except Exception as e:
            # Log the exception for better debugging
            print(f"Error clicking first locator: {e}")
            try:
                # Fallback to click the first matching element for elem_1
                self.ig.page.locator(elem_1).first().click()
            except Exception as e2:
                print(f"Error clicking fallback locator: {e2}")

    def go_to_next_posts(self):

        for _ in range(self.post_numbers):
            try:
                self.ig.page.get_by_role("button", name="Next", exact=True).click()
                self.load_more_comments()
            except:
                self.ig.page.locator("button").filter(has_text="Next").click()

            self.ig.pause(5000, 13000)

    def load_more_comments(self):
        for _ in range(self.load_more_comments_number):
            self.ig.get_by_role("button", name="Load more comments").nth(0).click()
            self.ig.pause(3000, 6000)

    def close_post_page(self):

        try:
            self.ig.page.get_by_role("button", name="Close").click()
            self.ig.account.add_cli('Close dont existsssss')
        except:
            self.base.go_to_home()

        self.ig.pause(1000, 2000)
