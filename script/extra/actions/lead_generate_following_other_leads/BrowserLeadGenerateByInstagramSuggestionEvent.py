from script.extra.helper import go_to_page
from script.models.EnrichedLead import get_free_enriched_lead
from script.extra.parsers.InstagramSuggestionParser import InstagramSuggestionParser
from script.models.Lead import Lead


class BrowserLeadGenerateByInstagramSuggestionEvent:
    ig = None
    command = None
    parser = None
    number_of_leads = 4
    listener = None

    def __init__(self, ig):
        self.ig = ig

    def add_listener(self):
        """Attach temporary listener for Instagram suggestions"""
        def on_response(response):
            if '/graphql/query' in response.url:
                try:
                    json_response = response.json()
                    self.process_response(json_response)
                except Exception as e:
                    self.ig.account.add_cli(f"Error parsing response: {e}")

        # Save listener reference to remove it later
        self.listener = on_response
        self.ig.page.on("response", self.listener)

    def remove_listener(self):
        """Detach listener when finished"""
        if self.listener:
            try:
                self.ig.page.remove_listener("response", self.listener)
                self.listener = None
            except Exception as e:
                self.ig.account.add_cli(f"Failed to remove listener: {e}")

    def process_response(self, json):
        self.parser = InstagramSuggestionParser(json, self.ig.account)

        try:
            self.parser.parse()
        except Exception as e:
            self.ig.account.add_cli(str(e))

        self.ig.account.add_cli(f'Found {len(self.parser.usernames)} leads...')
        self.insert_leads()

    def insert_leads(self):
        for username in self.parser.usernames:
            try:
                Lead.get_or_create(username=username)
            except Exception as e:
                self.ig.account.add_cli(f"Failed to insert lead {username}: {str(e)}")

    def init(self):
        self.ig.account.add_cli("Generating Leads by Instagram suggestion ...")

        for _ in range(self.number_of_leads):
            try:
                self.command = self.ig.account.create_command('generate lead by instagram suggestion', 'processing')
                self.generate_lead()
                self.command.update_cmd('state', 'success')
            except Exception as e:
                self.ig.account.add_cli("Failed to generate lead by page engagement: " + str(e))
                if self.command:
                    self.command.update_cmd('state', 'fail')

            self.ig.pause(4000, 5000)

    def generate_lead(self):
        # Add listener before navigation
        self.add_listener()

        lead = get_free_enriched_lead()
        go_to_page(self.ig, f'https://www.instagram.com/{lead.instagram_username}', "Lead's page")
        self.ig.pause(4000, 5000)

        # Remove listener after finishing
        self.remove_listener()
