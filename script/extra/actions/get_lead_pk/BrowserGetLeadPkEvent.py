from random import random

from script.extra.playwright.base_actions.SearchForAction import SearchForAction
from script.models.Lead import Lead
from script.models.Setting import Setting
from script.extra.parsers.LeadGetPkParser import LeadGetPkParser

import random
import re


class BrowserGetLeadPkEvent:
    command = None
    number_of_leads = None
    users = None
    lead = None

    def __init__(self, ig):
        self.ig = ig
        self.search_for = SearchForAction(self.ig)
        self.category_model = self.ig.account.category

        min = Setting.get_value('Min leads to get pk', 10)
        max = Setting.get_value('Max leads to get pk', 15)

        self.number_of_leads = random.randint(min, max)
        self.ig.page.on("response", lambda response: self.handle_response(response))

    def handle_response(self, response):
        if 'graphql/query' in response.url:
            json_response = response.json()
            self.process_response(json_response)

    def process_response(self, json):
        self.users = LeadGetPkParser(json, self.ig.account).parse()

        for user in self.users:
            user = user["user"]
            if user['username'] == self.lead.username:
                self.ig.account.add_cli(f"Matched user : {user['username']}")
                self.lead.update_instagram_id(user["pk"])

    def init(self):
        self.ig.account.add_cli(f"Getting Leads pk ...")

        leads = Lead.get_without_pk_leads(self.number_of_leads)

        try:
            self.ig.page.get_by_role("link", name="Search Search").click(timeout=3000)
        except:
            self.ig.page.get_by_role("link", name="Search").click(timeout=3000)

        self.ig.pause(3000, 3500)

        for self.lead in leads:
            self.fill_phrase(self.lead.username)
            self.ig.pause(3000, 3500)

    def fill_phrase(self, phrase):
        try:
            self.ig.page.get_by_placeholder("Search").fill('')
            self.ig.page.get_by_placeholder("Search").fill(phrase)
        except:
            self.ig.page.locator("input[aria-label='Search input']").first.fill('')
            self.ig.page.locator("input[aria-label='Search input']").first.fill(phrase)
