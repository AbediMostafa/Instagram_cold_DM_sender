from script.extra.events.browser_events.BrowserBaseEvent import BrowserBaseEvent
from script.extra.playwright.base_actions.GoToThreadsAction import GoToThreadsAction
from script.extra.playwright.base_actions.TurnOnNotificationAction import TurnOnNotificationAction
from script.extra.playwright.base_actions.ClickOnNewMessageAction import ClickOnNewMessageAction
from script.extra.playwright.base_actions.FillAccountSearchForDmAction import FillAccountSearchForDmAction
from script.extra.playwright.base_actions.ClickOnFirstAccountSearchForDmAction import \
    ClickOnFirstAccountSearchForDmAction
from script.extra.playwright.base_actions.ClickOnChatAction import ClickOnChatAction
from script.extra.playwright.base_actions.ClickOnSendMessageAction import ClickOnSendMessageAction
from script.extra.playwright.base_actions.GoToAccountPageAction import GoToAccountPageAction
from script.extra.playwright.base_actions.GetThreadUrlAction import GetThreadUrlAction
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.ErrorIndicators import ErrorIndicators
from script.models.Lead import Lead
from script.models.Spintax import Spintax
from spintax import spin
from script.extra.helper import go_to_page
from script.models.Account import Account
from urllib.parse import parse_qs
from script.models.Tag import Tag
from script.models.Taggable import Taggable

BATCH_SIZE = 15


class AddToGroup:
    listener = None
    api_usernames = []

    def __init__(self, ig):
        self.ig = ig
        self._setup_listener()

        # Get the account's category to send spintax with that category to the lead with the same category
        # self.category_model = self.ig.account.category
        # self.category = self.category_model.title if self.category_model else None

    def init(self):

        urls = [
            'https://www.instagram.com/direct/t/1152609427940275/',  # 1
            'https://www.instagram.com/direct/t/1000281282787780/',  # 2
            'https://www.instagram.com/direct/t/2547102745703306/',  # 3
            'https://www.instagram.com/direct/t/1024491809947597/',  # 4
            'https://www.instagram.com/direct/t/1096623009445917/',  # 5
            'https://www.instagram.com/direct/t/1035038942240663/',  # 6
            'https://www.instagram.com/direct/t/1546640413573142/',  # 7
            'https://www.instagram.com/direct/t/1013122784758790/',  # 8
            'https://www.instagram.com/direct/t/1427966025880532/',  # 9
            'https://www.instagram.com/direct/t/1180820728450645/',  # 10
            'https://www.instagram.com/direct/t/4594983004068784/',  # 11
            'https://www.instagram.com/direct/t/1580131110157720/',  # 12
            'https://www.instagram.com/direct/t/1565090271823114/',  # 13
            'https://www.instagram.com/direct/t/1759544428807024/',  # 14
            'https://www.instagram.com/direct/t/1577911837061268/',  # 15
            'https://www.instagram.com/direct/t/2476116716205177/',  # 16
            'https://www.instagram.com/direct/t/1557055409281602/',  # 17
            'https://www.instagram.com/direct/t/1808493737188387/',  # 18
            'https://www.instagram.com/direct/t/1831113368301389/',  # 19
            'https://www.instagram.com/direct/t/796297220172224/'  # 20
        ]

        urls = [
            # 'https://www.instagram.com/direct/t/1820077392337174/', #20 -->248
            # 'https://www.instagram.com/direct/t/1057836507151845/', #19 -->max
            # 'https://www.instagram.com/direct/t/1765222088138849/', #18 -->248
            # 'https://www.instagram.com/direct/t/1645569313949193/', #17-->max
            # 'https://www.instagram.com/direct/t/1953917735295052/', #16 -->max
            # 'https://www.instagram.com/direct/t/1443482307595951/', #15 --> 151
            # 'https://www.instagram.com/direct/t/1492630149029542/', #14-->248
            # 'https://www.instagram.com/direct/t/1860172995426045/', #13 -->248
            'https://www.instagram.com/direct/t/1061646739788294/', #12 -->234
            # 'https://www.instagram.com/direct/t/1071113032057612/', #11 -->248
            # 'https://www.instagram.com/direct/t/1054794777521889/', #10 -->max
            # 'https://www.instagram.com/direct/t/1085199887208934/', #9-->248
            # 'https://www.instagram.com/direct/t/1949706019052340/', #8-->248
            'https://www.instagram.com/direct/t/2273130870170281/', #7-->232
            # 'https://www.instagram.com/direct/t/1241487078110607/', #6-->248
            # 'https://www.instagram.com/direct/t/1933169584046769/', #5-->248
            # 'https://www.instagram.com/direct/t/1086470653919050/', #4-->max
            # 'https://www.instagram.com/direct/t/1731522777963357/', #3-->max
            'https://www.instagram.com/direct/t/1589156179446000/', #2-->245
            # 'https://www.instagram.com/direct/t/1389516563314411/', #1-->248
        ]

        web_usernames = [
            "ary._amnin",
            "le.eanln7246",
            "tiago_rr53.77",
            "madinaa_jpokec2",
            "mkuhamm4d27",
            "_b.vijayyz._",
            "bihvcd7.1",
            "thegoldenwizardbjookprize",
            "mr_saya___007",
            "harqinibk_10",
            "tp.toi_letroll",
            "puransuthar20c15",
            "iraqui_tariquet75",
            "meikizedek_son_ofz_iam",
            "ms.deniqii",
            "carotlline_rodriguez",
            "katharina.bmrand",
            "angvgeel_____",
            "amb2ikkk",
            "br626.3",
            "arunm_andal1851",
            "sydnenymonmon",
            "annkisiel4l",
            "afsane_hbarekat",
            "alaa_ikero",
            "dirimuom",
            "alliesdeczorandmore",
            "danieloliveira__ns",
            "bihvcd7.6",
            "dldbshgh09",
            "abdolla.shwirvash",
            "anas_architekct24",
            "erro.r___.userrname",
            "k_aatkakes",
            "parmislesetoilegs_",
            "iremunalyilma_zer",
            "ayala.4118",
            "81_luisa4a",
            "trishirajg.exe",
            "admiralhippeyr_",
            "devy_ffauji",
            "vbnoui6.6",
            "adhz7909",
            "arlmnn.ma",
            "skyj_sirisak",
            "alli_the_bookaholicc13",
            "syfh_r10",
            "jonovicycc_15",
            "meinkyufrom",
            "iymad_qadi",
            "crazy.boyl001133",
            "njuggty8.9",
            "sumo.bjrr",
            "autumn_ijir.an",
            "itzsmwaura",
            "faustino50mase1",
            "arcos_qserviss",
            "jlonguitow8a",
            "oseama.alabdullahh",
            "jxndosnn",
            "aha_na_kuchupu",
            "at.design.studizo24",
            "gj.60023",
            "mochtriprasetieyawan",
            "scebbeelholm",
            "bihvcd7.3",
            "floreshurtadodeavid",
            "bayardob_urgos",
            "p0rwal_khnushi",
            "tiloor12355",
            "hsuchignbo",
            "thesonu.khann",
            "logam_cipctaa",
            "beckjstevefns",
            "cocchohector",
            "shiva_pradhan__gurjar",
            "matip_gf.44",
            "cut_toanicka",
            "gamebterminalnash",
            "veronicamullerarbquitetura",
            "guldamla_defsign",
            "ali_avkimran",
            "xiao_xian._.0o6",
            "original_tshuepho",
            "a_m_nd_",
            "rojaklpenro",
            "prodesign.fuy",
            "stilcodisposal",
            "artee_reali",
            "_rasoul.ssarafraz_",
            "_ruzzxzi",
            "alison_uw5.88",
            "tig.er_madride",
            "259_jofuarrox",
            "cassobuuuu",
            "zubaid_dirskse_",
            "abby1p00381",
            "_s0sunthesinee",
            "liss_ve8lasquez_c",
            "aryanmzacki",
            "_team_lim.on",
            "shredatheome",
            "teot1eocoli8",
            "lilrayofsuuvnshinee",
            "stephix5708",
            "one_lenz_.view",
            "maxnyr_ays",
            "anto_em.c_nia",
            "jdulissiri",
            "anitankaira",
            "lucas___dz66",
            "aqn_afdlh",
            "054_alffry",
            "sa.rah_sergent15",
            "tiago_rr53.44",
            "carlan__val",
            "damlaczzzg",
            "tetsuroyoshsino",
            "l2ah.cen3223",
            "may_kel45",
            "joshuarzkiy",
            "adytson.rh",
            "farideytres.7",
            "vierr.ig.riv",
            "sa_rtorial___la",
            "aster3225633",
            "jahir_flores_deev",
            "2spazzed.1.3_",
            "_ade_risdwan",
            "k_amalmzp",
            "dian_lestagri92",
            "n.ishanth_joel_",
            "l_a_cidi",
            "bhgcdghy",
            "velominaru.ntung_",
            "_aiini.20",
            "moek_htet_thar_",
            "ftam.b971",
            "sisterswho_areadtogether",
            "sunst.arpapa",
            "sibol12999",
            "vkarpa_ra",
            "chemrryntr123",
            "_ana_s.w_ara._",
            "z_.zzx990",
            "may_kel4555",
            "cedrsayoussef",
            "nabder.robert",
            "yng._sacyhin48",
            "safa2._azimi",
            "a_twal147",
            "gmtsyubtime",
            "l_sancheiz612",
            "nishane43957",
            "jace124x",
            "aimlessajmes",
            "davidni.hil_",
            "msmariaher.ndon",
            "_amirhosnein_mosavi",
            "cou.ntry_gun_lover_man",
            "malen_aa12466",
            "xx_xibgdg.rni",
            "_themarziej_",
            "im.kaoerw",
            "5kakrl_5",
            "massoud_malekpanah",
            "azzaaa_2s0",
            "itz_cute_boy_56678",
            "anikett_k_s",
            "dan.ardelean_2l7",
            "qamila_611",
            "may_kel4544",
            "casl_tor0ias",
            "aadituya_batham_07",
            "mojtuaba.abedi.359",
            "gax573r",
            "prod.b7y.gusta",
            "meuble_gargsouri",
            "devqender__pvt",
            "ajycan.b17",
            "pcond_test",
            "jackjones44770",
            "rrrhwei999",
            "dee_pakgaur11",
            "azizahainul2_",
            "j_dallia1h",
            "_t.x_.w.mii_",
            "gulmiraergausheva3839",
            "loxnewolf_danz",
            "bihan_jiya22",
            "reiriiheree_",
            "anclal_k",
            "darnio_pinkman",
            "joeremie.ndaka",
            "intslemegs",
            "style2dbybeck",
            "rifal_7coders",
            "aileejnchen._",
            "krr.isna9803",
            "the_thomas_fbkk",
            "reda_ef.z",
            "saida_h.synovaaa",
            "zhujam06803",
            "martinely_18.33",
            "far0hanpriambudii",
            "addictedto.hoop",
            "nic_o.not.nicho",
            "ll_k1zlq",
            "me.rlo_10070",
            "ethan.k_up",
            "zohre_mng90",
            "9trefdfen",
            "mahyarncarpet",
            "mazriedjourno",
            "cutipie__queen_g1433",
            "imcsamjutt",
            "rathiomprarkash87",
            "m_thompsoon9911",
            "sonia.mrflores",
            "wloekserc",
            "terashimakikakyu",
            "euelifunvr",
            "being_.pragatiii",
            "radinpourhos_sein",
            "alison_uw5.99",
            "tanxaz_zarie",
            "kawt.arc3620",
            "pepcini.e",
            "elvwis27x",
            "wendyopa.checo_",
            "bhgcdghy.7",
            "uzxair_chishti_",
            "y.eslam_artstudio",
            "xpozpz3d",
            "m__sobkirovich",
            "ashor5ii_a",
            "fabioranier_ii",
            "aldair1v2.s",
            "k.magyyaaa",
            "mhd_sthakil_",
            "sulreymankesgn1903",
            "chunkytokez45",
            "celineu.nica",
            "rafdh_sai76",
            "pinto_q0p.22",
            "james49612x7",
            "utopizk.u",
            "argh.charlgie",
            "bmqktfjg",
            "_oaiini.20",
            "katiagomes2019abb",
            "lunitapuntoeistrella",
            "dannyp_medina2805",
        ];

        # leads = Lead.get_leads_for_dm(self.ig.account, self.ig.account.current_chunk_dm)

        # usernames = [
        #     account.username
        #     for account in (
        #         Account
        #         .select()
        #         .where(Account.instagram_state == 'active')
        #         .join(
        #             Taggable,
        #             on=(
        #                     (Taggable.taggable_id == Account.id) &
        #                     (Taggable.taggable_type == Taggable.get_taggable_class('Account'))
        #             )
        #         )
        #         .join(Tag)
        #         .where(Tag.title == 'android')
        #     )
        # ]

        for url in urls:
            self.ig.account.add_cli('Going to url ...')
            go_to_page(self.ig, url)

            self.ig.pause(6000, 7000)
            self.ig.turn_on_notif()
            self.ig.pause(4000, 4500)
            #
            # accounts = Account.select().where(Account.service_id == 7)
            # web_usernames = [account.username for account in accounts]
            # mobile = ['edward_raising_1', 'k_f_kvrz_f2103']
            #
            # web_usernames.extend(mobile)
            #
            usernames = [u for u in web_usernames if u not in set(self.api_usernames)]

            print('USERNAMES ARE +++++++++++++++++++++++++++++')
            print(usernames)

            # Open Conversation information
            try:
                self.ig.page.get_by_label("Conversation information").click(timeout=5000)
            except:
                self.ig.page.locator(
                    "div[role='button']:has(svg[aria-label='Conversation information'])"
                ).click()

            self.ig.pause(3000, 4000)

            # Process usernames in batches of 15
            for start in range(0, len(usernames), BATCH_SIZE):

                # Open Add people
                self.ig.pause(3000, 4000)

                try:
                    self.ig.page.get_by_role("button", name="Add people").click(timeout=5000)
                except:
                    self.ig.page.locator("text='Add people'").click()

                self.ig.pause(4000, 5500)

                messages = [
                    'Group limit reached',
                    "reached the maximum number of members.",
                ]

                if self.ig.is_visible_by_texts(messages):
                    self.ig.account.add_cli("You've reached the maximum number of members.")
                    break

                self.ig.pause(3000, 4000)

                batch = usernames[start:start + BATCH_SIZE]

                for username in batch:

                    search = self.ig.page.get_by_placeholder("Search...")

                    search.fill("")
                    self.ig.pause(300, 600)

                    search.fill(username)
                    self.ig.pause(4000, 5000)

                    if self.ig.is_visible_by_text("No results found"):
                        self.ig.account.add_cli(f"{username} - no results")
                        search.fill("")
                        continue

                    user = self.ig.page.locator("[role='option']").filter(has_text=username)

                    if user.count():
                        self.ig.account.add_cli(f"{username} found")
                        user.first.click()
                        self.ig.pause(2000, 3000)

                    search.fill("")

                # Click Next
                self.ig.account.add_cli("Clicking Next")

                try:
                    self.ig.page.get_by_role("button", name="Next").click(timeout=5000)
                    self.ig.account.add_cli("Could click Next")

                except:
                    try:
                        self.ig.account.add_cli("Could NOT click Next")
                        self.ig.page.locator("text='Next'").click(timeout=5000)
                    except:
                        pass

                self.ig.pause(5000, 7000)
                self.ig.account.add_cli("Pressing Escape")
                self.ig.page.keyboard.press("Escape")
                self.ig.pause(1000, 2000)

                # Last batch doesn't need Next
                if start + BATCH_SIZE >= len(usernames):
                    break

    def _setup_listener(self):
        """Listen for profile response"""

        def on_response(response):
            if 'api/graphql' not in response.url:
                return

            post_data = response.request.post_data

            if not post_data:
                self.ig.account.add_cli("There's no Post data ... ")
                return

            parsed = parse_qs(post_data, keep_blank_values=True)
            fb_api_name = parsed.get('fb_api_req_friendly_name', [''])[0]

            if 'IGDInboxHeaderOffMsysQuery' not in fb_api_name:
                return

            response = response.json()
            data = response.get("data", {})
            xdt = data.get("get_slide_thread_nullable", {})
            edges = xdt.get("as_ig_direct_thread", {})
            users = edges.get("users", {})

            self.api_usernames = [user.get('username') for user in users]

            self.ig.account.add_cli(f'username count  : {len(self.api_usernames)}')

        self.listener = on_response
        self.ig.page.on('response', on_response)
