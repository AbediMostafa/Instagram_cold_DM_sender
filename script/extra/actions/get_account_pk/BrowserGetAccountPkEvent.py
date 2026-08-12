from random import random
from script.extra.helper import go_to_page

from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.models.Lead import Lead
from script.models.Account import Account
from script.models.Setting import Setting
from script.extra.parsers.LeadGetPkParser import LeadGetPkParser

import random
import re


class BrowserGetAccountPkEvent:
    command = None
    number_of_leads = None
    users = None
    lead = None

    def __init__(self, ig):
        self.ig = ig
        self.search_for = SearchForAction(self.ig)
        self.category_model = self.ig.account.category

        self.accounts = Account.select().where(
            (Account.service_id == 6) &
            (Account.instagram_id == None)
        )
        self.ig.page.on("response", lambda response: self.handle_response(response))

    def handle_response(self, response):
        if 'api/graphql' in response.url:
            json_response = response.json()
            user = json_response.get('data', {}).get('user', {})

            if not user:
                return

            username = user.get('username')
            instagram_id = user.get('pk')

            print(f'Real username : {username} with PK : {instagram_id}')

            account = Account.get(Account.username == username)
            account.instagram_id = instagram_id
            account.save()


    def init(self):
        self.ig.account.add_cli(f"Getting account pk ...")

        for account in self.accounts:
            go_to_page(self.ig, f'https://www.instagram.com/{account.username}')
            self.ig.pause(5000, 7000)

