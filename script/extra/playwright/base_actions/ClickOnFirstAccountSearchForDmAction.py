from .BaseAction import BaseAction


class ClickOnFirstAccountSearchForDmAction(BaseAction):
    first_searched_user_locator = 'div.x9f619.xjbqb8w.x78zum5.x168nmei>div.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n'
    first_searched_user_alternative_locator = 'div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1pi30zi.x1swvt13.xwib8y2.x1y1aw1k.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.x1qjc9v5.x1oa3qoh.x1nhvcw1'

    def start(self):
        try:
            self.ig.page.locator(self.first_searched_user_locator).first.click(timeout=3000)
        except:
            self.ig.account.add_cli('Trying second locator to click on first username ...')
            self.ig.page.locator(self.first_searched_user_alternative_locator).first.click(timeout=3000)
