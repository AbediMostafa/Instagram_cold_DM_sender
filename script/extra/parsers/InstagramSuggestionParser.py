class InstagramSuggestionParser:
    json = None
    account = None
    usernames = []

    def __init__(self, json, account):
        self.json = json
        self.account = account
        self.usernames = []  # Initialize usernames list

    def parse(self):

        if "data" in self.json:
            if "xdt_api__v1__discover__chaining" in self.json["data"]:
                if "users" in self.json["data"]["xdt_api__v1__discover__chaining"]:
                    for user in self.json["data"]["xdt_api__v1__discover__chaining"]["users"]:
                        self.usernames.append(user["username"])
