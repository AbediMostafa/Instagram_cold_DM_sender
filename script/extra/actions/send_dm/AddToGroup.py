from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.playwright.base_actions.GoToThreadsAction import GoToThreadsAction
from script.extra.playwright.base_actions.TurnOnNotificationAction import TurnOnNotificationAction
from script.extra.playwright.base_actions.ClickOnNewMessageAction import ClickOnNewMessageAction
from script.extra.playwright.base_actions.FillAccountSearchForDmAction import FillAccountSearchForDmAction
from script.extra.playwright.base_actions.ClickOnFirstAccountSearchForDmAction import \
    ClickOnFirstAccountSearchForDmAction
from script.extra.playwright.base_actions.ClickOnChatAction import ClickOnChatAction
from script.extra.playwright.base_actions.ClickOnSendMessageAction import ClickOnSendMessageAction
from script.extra.playwright.base_actions.GoToAccountPageAction import GoToAccountPageAction
from script.extra.playwright.base_actions.GetThreadUrlAction import GetThreadUrlAction
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.models.Lead import Lead
from script.models.Spintax import Spintax
from spintax import spin
from script.extra.helper import go_to_page
from script.models.Account import Account
from urllib.parse import parse_qs
from script.models.Tag import Tag
from script.models.Taggable import Taggable

BATCH_SIZE = 15


class AddToGroup:
    listener = None
    api_usernames = []

    def __init__(self, ig):
        self.ig = ig
        self._setup_listener()

        # Get the account's category to send spintax with that category to the lead with the same category
        # self.category_model = self.ig.account.category
        # self.category = self.category_model.title if self.category_model else None

    def init(self):

        urls = [
            # 'https://www.instagram.com/direct/t/1152609427940275/',  # 1
            'https://www.instagram.com/direct/t/1000281282787780/',  # 2
            'https://www.instagram.com/direct/t/2547102745703306/',  # 3
            'https://www.instagram.com/direct/t/1024491809947597/',  # 4
            'https://www.instagram.com/direct/t/1096623009445917/',  # 5
            'https://www.instagram.com/direct/t/1035038942240663/',  # 6
            'https://www.instagram.com/direct/t/1546640413573142/',  # 7
            'https://www.instagram.com/direct/t/1013122784758790/',  # 8
            'https://www.instagram.com/direct/t/1427966025880532/',  # 9
            'https://www.instagram.com/direct/t/1180820728450645/',  # 10
            'https://www.instagram.com/direct/t/4594983004068784/',  # 11
            'https://www.instagram.com/direct/t/1580131110157720/',  # 12
            'https://www.instagram.com/direct/t/1565090271823114/',  # 13
            'https://www.instagram.com/direct/t/1759544428807024/',  # 14
            'https://www.instagram.com/direct/t/1577911837061268/',  # 15
            'https://www.instagram.com/direct/t/2476116716205177/',  # 16
            'https://www.instagram.com/direct/t/1557055409281602/',  # 17
            'https://www.instagram.com/direct/t/1808493737188387/',  # 18
            'https://www.instagram.com/direct/t/1831113368301389/',  # 19
            'https://www.instagram.com/direct/t/796297220172224/'  # 20
        ]

        usernames = [
            'kiichiq23',
            'bang_dwidit',
            'lacerdaj_livia',
            'nik5c9397',
            'nivedi_ta_kuragund',
            'marshmell_o_gwl',
            'thesebastian6465',
            'l_j_us.tin',
            'mrathilde.m.n',
            'thesebastian6411',
            'ahmt._cnb',
            'goldfishschou',
            'frake_jinnat',
            'euger.vasquez.3',
            'ylon_2b',
            'kanza_vfarhan',
            'bhaekti_with_ansh',
        ]
        # leads = Lead.get_leads_for_dm(self.ig.account, self.ig.account.current_chunk_dm)

        # usernames = [
        #     account.username
        #     for account in (
        #         Account
        #         .select()
        #         .where(Account.instagram_state == 'active')
        #         .join(
        #             Taggable,
        #             on=(
        #                     (Taggable.taggable_id == Account.id) &
        #                     (Taggable.taggable_type == Taggable.get_taggable_class('Account'))
        #             )
        #         )
        #         .join(Tag)
        #         .where(Tag.title == 'android')
        #     )
        # ]

        for url in urls:
            self.ig.account.add_cli('Going to url ...')
            go_to_page(self.ig, url)

            self.ig.pause(6000, 7000)
            self.ig.turn_on_notif()
            self.ig.pause(4000, 4500)
            #
            # accounts = Account.select().where(Account.service_id == 7)
            # web_usernames = [account.username for account in accounts]
            # mobile = ['edward_raising_1', 'k_f_kvrz_f2103']
            #
            # web_usernames.extend(mobile)
            #
            # usernames = [u for u in web_usernames if u not in set(self.api_usernames)]

            # Open Conversation information
            try:
                self.ig.page.get_by_label("Conversation information").click(timeout=5000)
            except:
                self.ig.page.locator(
                    "div[role='button']:has(svg[aria-label='Conversation information'])"
                ).click()

            self.ig.pause(3000, 4000)

            # Process usernames in batches of 15
            for start in range(0, len(usernames), BATCH_SIZE):

                # Open Add people
                self.ig.pause(3000, 4000)

                try:
                    self.ig.page.get_by_role("button", name="Add people").click(timeout=5000)
                except:
                    self.ig.page.locator("text='Add people'").click()

                self.ig.pause(4000, 5500)

                messages = [
                    'Group limit reached',
                    "reached the maximum number of members.",
                ]

                if self.ig.is_visible_by_texts(messages):
                    self.ig.account.add_cli("You've reached the maximum number of members.")
                    break

                self.ig.pause(3000, 4000)

                batch = usernames[start:start + BATCH_SIZE]

                for username in batch:

                    search = self.ig.page.get_by_placeholder("Search...")

                    search.fill("")
                    self.ig.pause(300, 600)

                    search.fill(username)
                    self.ig.pause(4000, 5000)

                    if self.ig.is_visible_by_text("No results found"):
                        self.ig.account.add_cli(f"{username} - no results")
                        search.fill("")
                        continue

                    user = self.ig.page.locator("[role='option']").filter(has_text=username)

                    if user.count():
                        self.ig.account.add_cli(f"{username} found")
                        user.first.click()
                        self.ig.pause(2000, 3000)

                    search.fill("")

                # Click Next
                self.ig.account.add_cli("Clicking Next")

                try:
                    self.ig.page.get_by_role("button", name="Next").click(timeout=5000)
                    self.ig.account.add_cli("Could click Next")

                except:
                    try:
                        self.ig.account.add_cli("Could NOT click Next")
                        self.ig.page.locator("text='Next'").click(timeout=5000)
                    except:
                        pass

                self.ig.pause(5000, 7000)
                self.ig.account.add_cli("Pressing Escape")
                self.ig.page.keyboard.press("Escape")
                self.ig.pause(1000, 2000)

                # Last batch doesn't need Next
                if start + BATCH_SIZE >= len(usernames):
                    break

    def _setup_listener(self):
        """Listen for profile response"""

        def on_response(response):
            if 'api/graphql' not in response.url:
                return

            post_data = response.request.post_data

            if not post_data:
                self.ig.account.add_cli("There's no Post data ... ")
                return

            parsed = parse_qs(post_data, keep_blank_values=True)
            fb_api_name = parsed.get('fb_api_req_friendly_name', [''])[0]

            if 'IGDInboxHeaderOffMsysQuery' not in fb_api_name:
                return

            response = response.json()
            data = response.get("data", {})
            xdt = data.get("get_slide_thread_nullable", {})
            edges = xdt.get("as_ig_direct_thread", {})
            users = edges.get("users", {})

            self.api_usernames = [user.get('username') for user in users]

            self.ig.account.add_cli(f'username count  : {len(self.api_usernames)}')

        self.listener = on_response
        self.ig.page.on('response', on_response)
