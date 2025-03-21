class FollowersParser:
    json = None
    account = None
    usernames = []

    def __init__(self, json, account):
        self.json = json
        self.account = account
        self.usernames = []  # Initialize usernames list

    def parse(self):
        for user in self.json["users"]:
            self.usernames.append(user["username"])
