from .BaseAction import BaseAction


class GetThreadUrlAction(BaseAction):

    def start(self):
        import re
        url = self.ig.page.url

        # Use regex to extract the thread_id after "/t/" and before a possible trailing slash
        match = re.search(r'/t/(\d+)', url)

        if match:
            # Return the thread_id if found
            return match.group(1)
        else:
            raise ValueError("Thread ID not found in URL")
