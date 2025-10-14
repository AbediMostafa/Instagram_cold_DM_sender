from script.extra.helper import go_to_page
from script.extra.playwright.base_actions.GoToProfilePageAction import GoToProfilePageAction
import re
import random
import string


def random_word():
    length = random.randint(5, 10)  # random length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

class BrowserActivate2faCodeEvent:
    command = None
    add_button_locator = 'span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1sfkdl8.xurcqga.x3vd66c.xhqx0jl.x1fey0fg.x1yc453h.xudqn12.x3x7a5m'
    two_factor_locator = 'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xf7dkkf.xv54qhq.x16grhtn span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x'
    name_input = 'input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.x1o3jo1z.x16stqrj.xv5lvn5.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.xzsf02u.x1lliihq.x15h3p50.x10emqs4.x1vr9vpq.x1iyjqo2.x10d0gm4.x1fhayk4.x16wdlz0.x3cjxhe.xe9ewy2.x11lt19s.xeuugli.xlyipyv.x1hcrkkg.xfvqz1d.x12vv892.x1hu168l.xttzon8.x1sfh74k.x3fqe8q.x185fvkj.x1p97g3g'
    code_input = 'div.x6s0dn4.x78zum5.x1qughib.xh8yej3 input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.x1o3jo1z.x16stqrj.xv5lvn5.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x972fbf'

    def __init__(self, ig):
        self.ig = ig

    def init(self):

        try:
            self.ig.account.add_cli('Activating 2fa code ...')
            self.before_change_hook()
            self.change_hook()
            self.after_change_hook()

        except Exception as e:
            import traceback

            if self.command:
                self.command.update_cmd('state', 'fail')
            self.ig.account.add_cli(f"Problem activating two factor : {str(e)}")
            self.ig.account.add_log(traceback.format_exc())

        finally:
            go_to_page(self.ig, f'https://www.instagram.com/', "Home")
            self.ig.pause(3000, 4000)

    def before_change_hook(self):
        self.command = self.ig.account.create_command('activate 2fa code', 'processing')

    def change_hook(self):

        GoToProfilePageAction(self.ig).start()
        go_to_page(self.ig, 'https://accountscenter.instagram.com/password_and_security/two_factor/', "Two factor")
        self.ig.pause(5000, 6500)
        self.ig.page.get_by_text(self.ig.account.username).click(timeout=3000)
        self.ig.pause(5000, 6500)

        self.handle_errors()

        if self.ig.is_visible_by_text('Two-factor authentication is on'):
            self.two_factor_exists()

        if self.ig.is_visible_by_text('Help protect your account'):
            self.two_factor_doesnt_exist()

        two_factor = self.ig.page.locator(self.two_factor_locator).inner_text()
        self.ig.account.add_cli(f'Two factor {two_factor}')

        self.ig.page.get_by_role("button", name="Next").click(timeout=5000)
        self.ig.account.set('secret_key', two_factor)

        self.ig.pause(6000, 7000)
        key = self.ig.account.get_verification_code(two_factor)
        self.ig.account.add_cli(f'key : {key}')

        self.ig.page.get_by_label('Enter code').fill(key, timeout=3000)
        self.ig.pause(4000, 5000)

        self.ig.page.get_by_role("button", name="Next").click(timeout=5000)
        self.ig.pause(7000, 8000)
        self.ig.page.get_by_role("button", name="Done").click(timeout=5000)
        self.ig.pause(7000, 8000)

    def handle_errors(self):
        if self.ig.is_visible_by_text('This content is no longer available') or self.ig.is_visible_by_text(
                "You can't make this change") or self.ig.is_visible_by_text(
                "This is because we noticed you are using a device you"):
            raise Exception("You can't make this change at the moment")

        if self.ig.is_visible_by_text('GraphQL request to generate TOTP key failed.'):
            raise Exception('GraphQL request to generate TOTP key failed.')

    def two_factor_exists(self):
        self.ig.page.get_by_text('Authentication app').nth(0).click(timeout=3000)
        self.ig.pause(4000, 6500)

        try:
            self.ig.page.locator(self.add_button_locator).click(timeout=3000)
            self.ig.account.add_cli('Adding another device')
            self.ig.pause(7000, 8000)

        except:
            self.ig.account.add_cli('another device dont exists')

        try:
            word = random_word()
            self.ig.page.get_by_label("Name", exact=True).fill(word, timeout=3000)
            self.ig.account.add_cli('Adding device name')
            self.ig.pause(7000, 8000)

        except:
            self.ig.account.add_cli('Device input dont exists(first method)')

            try:
                self.ig.page.locator(self.name_input).fill(word, timeout=3000)
            except:
                pass

        self.ig.page.get_by_role("button", name="Next").click(timeout=5000)
        self.ig.pause(6000, 6500)

    def two_factor_doesnt_exist(self):
        self.ig.page.get_by_role('button', name='Continue').click(timeout=3000)

    def after_change_hook(self):
        self.command.update_cmd('state', 'success')
        self.ig.account.set('two_factor_activated', 1)

















