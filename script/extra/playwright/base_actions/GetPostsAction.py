from .BaseAction import BaseAction
from .SearchForAction import SearchForAction


class GetPostsAction(BaseAction):

    def start(self):
        posts = self.ig.page.locator(
            'div._ac7v.x1f01sob.xcghwft.xat24cr.xzboxd6 > div.x1lliihq.x1n2onr6.xh8yej3.x4gyw5p')

        self.ig.account.add_cli(f'There are {posts.count()} posts')

        return posts
