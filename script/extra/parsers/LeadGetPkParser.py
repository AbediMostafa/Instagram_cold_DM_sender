class LeadGetPkParser:
    json = None
    account = None

    def __init__(self, json, account):
        self.json = json
        self.account = account

    def parse(self):
        try:
            return self.json["data"]["xdt_api__v1__fbsearch__topsearch_connection"]["users"]

        except Exception as e:
            return []
