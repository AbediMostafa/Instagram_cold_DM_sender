from urllib.parse import parse_qs, unquote_plus
import json
# x-root-field-name : xdt_api__v1__stories__reel__seen
# x-fb-friendly-name : PolarisStoriesV3SeenMutation
'''
__crn :comet.igweb.PolarisStoriesV3Route
fb_api_req_friendly_name : PolarisStoriesV3SeenMutation
variables : {"reelId":"1034063304","reelMediaId":"3843976907234762096","reelMediaOwnerId":"1034063304","reelMediaTakenAt":1772457771,"viewSeenAt":1772482306}
doc_id : 24372833149008516
'''
class RequestPayloadFetcherParser:
    response = None
    ig = None
    usernames = []
    payload = {}
    headers = {}
    cookies = {}

    def __init__(self, response, ig):
        self.response = response
        self.ig = ig

        self.parse_cookies()
        self.parse_payload()
        self.parse_headers()

    def parse(self):
        if "graphql/query" in self.response.url:

            self.ig.graphql_data = {
                "payload": self.payload,
                "headers": self.headers,
            }

            file_path = "payloaaaaaaaaaaaaaaaaaads.json"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.ig.graphql_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            self.ig.account.add_cli("Captured GraphQL request successfully")

    def parse_cookies(self):
        cookies_list = self.ig.context.cookies()
        self.cookies = [
            c for c in cookies_list
            if "instagram.com" in c.get("domain", "")
        ]

    def parse_headers(self):
        self.headers = dict(self.response.request.headers)

        cookie_string = "; ".join(
            f"{c['name']}={c['value']}" for c in self.cookies
        )

        self.headers["Accept"] = "*/*"
        self.headers["accept-language"] = "en-US,en;q=0.9"
        self.headers["content-type"] = "application/x-www-form-urlencoded"
        self.headers["origin"] = "https://www.instagram.com"
        self.headers["priority"] = "u=1, i"
        self.headers["sec-fetch-dest"] = "empty"
        self.headers["sec-fetch-mode"] = "cors"
        self.headers["sec-fetch-site"] = "same-origin"
        self.headers["cookie"] = cookie_string

        return self.headers

    def parse_payload(self):

        payload_str = self.response.request.post_data

        try:
            keys_to_delete = [
                "__crn",
                "fb_api_req_friendly_name",
                "variables",
                "doc_id",
            ]

            if not payload_str:
                payload_str =""

            parsed = parse_qs(payload_str, keep_blank_values=True)

            keys_to_remove = [
                k for k in parsed.keys()
                if k.startswith('route_urls') or '------WebKitFormBoundary' in k
            ]

            for k, v in parsed.items():

                if k in keys_to_delete:
                    continue

                if k in keys_to_remove:
                    continue

                value = v[0] if len(v) == 1 else v
                self.payload[k] = value

        except Exception as e:
            self.ig.account.add_cli(f'Problem getting response data: {str(e)}')
            raise Exception(f'Problem getting response data: {str(e)}')

        return self.payload
