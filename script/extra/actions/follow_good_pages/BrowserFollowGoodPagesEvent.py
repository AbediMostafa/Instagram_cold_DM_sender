class BrowserFollowGoodPagesEvent:
    def __init__(self, ig):
        self.ig = ig
        pass

    def init(self):
        self.click_on_search()

    def click_on_search(self):
        try:
            self.ig.page.get_by_role("link", name="Search Search").click()
            self.ig.account.add_cli('search clicked')
        except:
            self.ig.account.add_cli('Search doesnt exists')
            self.ig.page.locator(
                'span[aria-describedby=":ri:"] x9f619.x3nfvp2.xr9ek0c.xjpr12u.xo237n4.x6pnmvc.x7nr27j.x12dmmrz.xz9dl7a.xn6708d.xsag5q8.x1ye3gou.x80pfx3.x159b3zp.x1dn74xm.xif99yt.x172qv1o.x10djquj.x1lhsz42.xzauu7c.xdoji71').click(
                timeout=3000)

        self.ig.pause(2000, 3000)
