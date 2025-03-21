from script.extra.playwright.base_actions.SearchForAction import SearchForAction
import random


class BrowserFollowGoodPagesEvent:
    command = None
    good_pages = [
        'khamenei.ir.iran',
        'khamenei_ir.iran',
        'shahid.raisi.aziz',
        'ostad_aali_official',
        'drrafiei_ir',
        'fateminia',
        'ostadfarahzad',
        'bozorgan_sokhan2',
        'dr.saeedazizi.ir',
        'gharaati.tv.ir',
        'sarcheshmeh_nour',
        'saeedazizi_ir',
        'herzraouf',
        'hakim.kheirandish',
        'solok__1',
        'tabib.iranii',
        'dr_anusheeh',
        'behjat_tv',
        'salamatkade_sib',
        'akhlagh_ir',
        'moghis313'
    ]

    def __init__(self, ig):
        self.ig = ig
        self.search_for = SearchForAction(self.ig)
        self.category_model = self.ig.account.category

    def init(self):
        user = random.choice(self.good_pages)
        try:
            self.command = self.ig.account.create_command('follow good pages', 'processing',
                                                          category=self.category_model)
            self.search_for.start(user)
            self.ig.pause(4000, 5000)
            self.click_on_search(user)

            self.ig.page.get_by_role("button", name="Follow").click()
            self.ig.pause(3000, 4000)
            self.follow_all_suggested()
            self.command.update_cmd('state', 'success')

        except Exception as e:
            if self.command:
                self.command.update_cmd('state', 'fail')

    def click_on_search(self, user):
        try:
            self.ig.page.goto(f'https://www.instagram.com/{user}')

        except Exception as e:
            self.ig.account.add_cli(f'Problem clicking on first a lead_source {str(e)}')
            self.ig.page.locator(
                "div.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x6ikm8r.x1odjw0f.xh8yej3.xocp1fn a").first.click(timeout=4000)

        self.ig.pause(3000, 4000)

    def follow_all_suggested(self):
        follow_buttons = self.ig.page.query_selector_all('div[role="button"]:has-text("Follow")')
        self.ig.account.add_cli(f'{len(follow_buttons)} Follow buttons')

        first_five_buttons = follow_buttons if len(follow_buttons) < 4 else follow_buttons[:4]

        count = 0

        for button in first_five_buttons:
            count += 1
            self.ig.account.add_cli(f"Following suggested user for time : {count}")

            button.click(timeout=4000)
            self.ig.pause(1500, 3000)
