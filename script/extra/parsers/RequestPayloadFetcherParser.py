from urllib.parse import parse_qs


class RequestPayloadFetcherParser:
    """Parse and capture GraphQL request data for API calls"""

    EXCLUDED_PAYLOAD_KEYS = frozenset([
        "__crn",
        "fb_api_req_friendly_name",
        "variables",
        "doc_id",
    ])

    DEFAULT_HEADERS = {
        "Accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.instagram.com",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    def __init__(self, response, ig):
        self.response = response
        self.ig = ig
        self.payload = {}
        self.headers = {}
        self.cookies = []

    def parse(self):
        if "graphql/query" not in self.response.url:
            return False

        self._parse_cookies()
        self._parse_headers()
        self._parse_payload()

        self.ig.graphql_data = {
            "payload": self.payload,
            "headers": self.headers,
        }

        self.ig.account.add_cli("GraphQL data captured successfully")
        return True

    def _parse_cookies(self):
        try:
            self.cookies = [
                c for c in self.ig.context.cookies()
                if "instagram.com" in c.get("domain", "")
            ]
        except Exception:
            self.cookies = []

    def _parse_headers(self):
        self.headers = dict(self.response.request.headers)
        self.headers.update(self.DEFAULT_HEADERS)
        self.headers["cookie"] = "; ".join(
            f"{c['name']}={c['value']}" for c in self.cookies
        )

    def _parse_payload(self):
        payload_str = self.response.request.post_data or ""

        try:
            parsed = parse_qs(payload_str, keep_blank_values=True)

            for key, value in parsed.items():
                if key in self.EXCLUDED_PAYLOAD_KEYS:
                    continue
                if key.startswith('route_urls') or 'WebKitFormBoundary' in key:
                    continue

                self.payload[key] = value[0] if len(value) == 1 else value

        except Exception as e:
            self.ig.account.add_cli(f'Problem parsing payload: {str(e)}')