from time import sleep
from script.extra.instagram.browser.InstagramMiddleware import InstagramMiddleware
from script.extra.events.browser_events.BrowserGoToTargetAccountAndExplorePostsBase import \
    BrowserGoToTargetAccountAndExplorePostsBase
import random


class BrowserGoToTargetAccountAndExplorePosts:

    def __init__(self, ig, user_type='account', user_numbers=1, post_numbers=1, load_more_comments_number=1,
                 scroll_before_click=True, number_of_scrolls=1):
        self.ig = ig
        self.base_class = BrowserGoToTargetAccountAndExplorePostsBase(self.ig)

        self.user_type = user_type

        self.base_class.user_numbers = user_numbers
        self.base_class.post_numbers = post_numbers
        self.base_class.load_more_comments_number = load_more_comments_number
        self.base_class.scroll_before_click = scroll_before_click
        self.base_class.number_of_scrolls = number_of_scrolls

    def fire(self):

        if self.user_type == 'account':
            self.base_class.get_a_user_method = self.base_class.get_a_random_account

        elif self.user_type == 'lead':
            self.base_class.get_a_user_method = self.base_class.get_a_random_lead

        elif self.user_type == 'random_user':
            self.base_class.get_a_user_method = self.base_class.get_a_random_user

        self.base_class.fire()
