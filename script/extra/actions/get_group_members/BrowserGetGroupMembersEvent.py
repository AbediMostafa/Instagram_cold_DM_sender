from script.extra.helper import go_to_page
from script.models.Account import Account
from script.models.Taggable import tag_account
from script.models.Tag import get_or_create_tag
from urllib.parse import parse_qs

BATCH_SIZE = 15


class BrowserGetGroupMembersEvent:
    listener = None
    api_usernames = []

    def __init__(self, ig):
        self.ig = ig
        self._setup_listener()

    def init(self):

        urls = {
            'group_1': 'https://www.instagram.com/direct/t/1152609427940275/',  # 1
            'group_2': 'https://www.instagram.com/direct/t/1000281282787780/',  # 2
            'group_3': 'https://www.instagram.com/direct/t/2547102745703306/',  # 3
            'group_4': 'https://www.instagram.com/direct/t/1024491809947597/',  # 4
            'group_5': 'https://www.instagram.com/direct/t/1096623009445917/',  # 5
            'group_6': 'https://www.instagram.com/direct/t/1035038942240663/',  # 6
            'group_7': 'https://www.instagram.com/direct/t/1546640413573142/',  # 7
            'group_8': 'https://www.instagram.com/direct/t/1013122784758790/',  # 8
            'group_9': 'https://www.instagram.com/direct/t/1427966025880532/',  # 9
            'group_10': 'https://www.instagram.com/direct/t/1180820728450645/',  # 10
            'group_11': 'https://www.instagram.com/direct/t/4594983004068784/',  # 11
            'group_12': 'https://www.instagram.com/direct/t/1580131110157720/',  # 12
            'group_13': 'https://www.instagram.com/direct/t/1565090271823114/',  # 13
            'group_14': 'https://www.instagram.com/direct/t/1759544428807024/',  # 14
            'group_15': 'https://www.instagram.com/direct/t/1577911837061268/',  # 15
            'group_16': 'https://www.instagram.com/direct/t/2476116716205177/',  # 16
            'group_17': 'https://www.instagram.com/direct/t/1557055409281602/',  # 17
            'group_18': 'https://www.instagram.com/direct/t/1808493737188387/',  # 18
            'group_19': 'https://www.instagram.com/direct/t/1831113368301389/',  # 19
            'group_20': 'https://www.instagram.com/direct/t/796297220172224/'  # 20
        }

        for group_name, url in urls.items():

            self.api_usernames = []

            self.ig.account.add_cli(f'Opening {group_name}')
            go_to_page(self.ig, url)

            self.ig.pause(7000, 9000)

            # wait until listener fills api_usernames
            for _ in range(20):
                if self.api_usernames:
                    break
                self.ig.pause(500, 700)

            self.process_group(group_name)

    def process_group(self, group_name):

        usernames = list(set(self.api_usernames))

        if not usernames:
            self.ig.account.add_cli(f'{group_name}: No usernames found.')
            return

        accounts = (
            Account
            .select() 
            .where(Account.username.in_(usernames))
        )

        account_map = {
            account.username: account
            for account in accounts
        }

        missing = []

        group_tag = get_or_create_tag(group_name)
        web_share_tag = get_or_create_tag('web_share')

        for username in usernames:

            account = account_map.get(username)

            if account is None:
                missing.append(username)
                continue

            tag_account(account, group_tag)
            tag_account(account, web_share_tag)

        self.ig.account.add_cli(
            f'{group_name}: {len(account_map)} accounts found.'
        )

        self.ig.account.add_cli(
            f'{group_name}: {missing} accounts NOT found.'
        )

        self.ig.account.add_cli(
            f'{group_name}: {len(missing)} accounts NOT found.'
        )


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
