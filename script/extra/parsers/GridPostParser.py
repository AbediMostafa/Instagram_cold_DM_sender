class GridPostParser:
    json = None
    account = None
    medias = []
    usernames = []

    def __init__(self, json, account):
        self.json = json
        self.account = account
        self.medias = []  # Initialize medias list
        self.usernames = []  # Initialize usernames list

    def parse(self):
        for section in self.json["media_grid"]["sections"]:
            try:
                self.parse_section(section)
            except Exception as e:
                self.account.add_cli(f'Problem parsing section : {str(e)}')

        self.parse_media()

    def parse_section(self, section):

        if "layout_type" in section:
            if section["layout_type"] == "two_by_two_right":
                self.parse_two_by_two_right(section["layout_content"])

            if section["layout_type"] == "media_grid":
                self.parse_media_grid(section["layout_content"])

    def parse_media_grid(self, content):
        if "medias" in content:
            for media_obj in content["medias"]:
                self.medias.append(media_obj["media"])

    def parse_two_by_two_right(self, content):
        if "two_by_two_item" in content:
            if "channel" in content["two_by_two_item"]:
                self.medias.append(content["two_by_two_item"]["channel"]["media"])

        if "fill_items" in content:
            for item in content["fill_items"]:
                self.medias.append(item["media"])

    def parse_media(self):
        for media in self.medias:
            try:
                self.usernames.append(media["user"]["username"])
            except Exception as e:
                self.account.add_cli(f'Problem parsing media : {str(e)}')
