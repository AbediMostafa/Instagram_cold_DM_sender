from script.extra.helper import go_to_page
from script.models.EnrichedLead import get_free_enriched_lead
from script.extra.parsers.InstagramSuggestionParser import InstagramSuggestionParser

from script.models.Lead import Lead


class BrowserLeadGenerateByInstagramSuggestionEvent:
    ig = None
    command = None
    parser = None
    number_of_leads = 4

    def __init__(self, ig):
        self.ig = ig
        self.ig.page.on("response", lambda response: self.handle_response(response))

    def handle_response(self, response):
        if '/graphql/query' in response.url:
            json_response = response.json()
            self.process_response(json_response)

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
        lead = get_free_enriched_lead()
        go_to_page(self.ig, f'https://www.instagram.com/{lead.instagram_username}', "Lead's page")
        self.ig.pause(4000, 5000)

        pass
