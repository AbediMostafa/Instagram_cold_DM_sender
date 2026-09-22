<?php

use App\Classes\ProfileMaker;
use App\Http\Controllers\AccountController;
use App\Http\Controllers\AccountSpecController;
use App\Http\Controllers\AppConfigController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\CategoryController;
use App\Http\Controllers\CliController;
use App\Http\Controllers\ColorController;
use App\Http\Controllers\CommandController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\DmPostController;
use App\Http\Controllers\HashtagController;
use App\Http\Controllers\LeadController;
use App\Http\Controllers\LeadSourceController;
use App\Http\Controllers\LoomController;
use App\Http\Controllers\MessageController;
use App\Http\Controllers\ModuleController;
use App\Http\Controllers\OrderController;
use App\Http\Controllers\ProcessController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\ProxyController;
use App\Http\Controllers\ServiceController;
use App\Http\Controllers\SettingController;
use App\Http\Controllers\SpintaxController;
use App\Http\Controllers\TagController;
use App\Http\Controllers\TemplateController;
use App\Http\Controllers\ThreadController;
use App\Http\Controllers\TikTokLinkController;
use App\Http\Controllers\TikTokTagController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\WorkflowController;
use \App\Http\Controllers\DuoWorkFlowController;
use App\Models\Mobile;
use App\Models\Service;
use App\Models\Template;
use Carbon\Carbon;
use Dotenv\Dotenv;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Storage;
use Morilog\Jalali\Jalalian;
use PhpOffice\PhpSpreadsheet\IOFactory;
use Symfony\Component\HttpKernel\Exception\HttpException;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use \App\Models\Account;
use \App\Models\Proxy;
use \App\Models\Profile;
use \App\Models\Tag;
use \App\Models\Order;

Route::get('/', function () {
//    Device_2 ==> "evurasian_cookncrea" پست در تایم لاین
//    Device_1 ==> yzoehanaaa_ --> پست در تایم لاین
//    Device_5 ==> frake_jinnat --> پست در تایم لاین
});
Route::get('/test', function () {

    dd(Order::query()->get());
    $usernames = [
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
        "_ag.nauiils",
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
return [
  'url'=>'https://www.zoomit.ir'
];

    dump(
        count($usernames)
    );

    dd(
        Account::query()
            ->where('service_id', 10)
            ->where('instagram_state', 'active')
            ->count()
    );
//   $res = Http::withoutVerifying()->post("http://209.200.252.19/duo-workflow/start");
//    dd($res->json());

    $mobile = Mobile::query()
        ->find(5);

    dd(
        $mobile->accounts->pluck('username')->toArray()
    );

    dd(
        \App\Models\DuoWorkFlow::query()->get()
    );
    dd(
        \App\Models\Cli::query()->count()
    );
    dd('salam');

    $links = [
        'https://www.instagram.com/p/C9gw8NfMJKy/?igsh=MXB6a2NraTZld2NtMg==',
        'https://www.instagram.com/p/DaZHlJvotcW/?igsh=MXVpZWw3eDBjd3Bkdw==',
        'https://www.instagram.com/p/C3lOBchLukK/?igsh=MWE1ZDZybzYxZHQ5MA==',
        'https://www.instagram.com/p/C3h5z-9t2ft/?igsh=MTVhem5rMGN6Z3JybA==',
        'https://www.instagram.com/p/C3NMU1yNJdF/?igsh=NWEyZDNxenRvZWtk',
        'https://www.instagram.com/p/C9gw7KRspcR/?igsh=MWk4dXcxYW03M3FleA==',
    ];

    foreach ($links as $link) {
        $data = [
            'action' => 'add',
            'service' => 744,
            'quantity' => 100000,
            'link' => $link
        ];

        $res = Http::withoutVerifying()->post('http://192.142.4.29/api/v3', $data);

        dump($res->json());
    }


//    $usernames = [
//        'thesebastian6465',
//        'mrathilde.m.n',
//    ];
//
//    $accounts = Account::query()->whereIn('username', $usernames)
//
//        ->update([
//            'mobile_id'=>5
//        ]);
//
//    dd($accounts);
});


Route::post('login', [AuthController::class, 'login']);
Route::post('sign-out', [AuthController::class, 'signOut']);
Route::post('lead/api/export', [LeadController::class, 'exportApi']);
Route::post('categories/get-categories', [CategoryController::class, 'getCategories']);
Route::post('app-config', [AppConfigController::class, 'index']);
Route::post('account/get-proxy-api', [AccountController::class, 'getProxyApi']);
Route::post('account/change-profile-proxy-to-custom', [AccountController::class, 'changeProfileProxyToCustom']);
Route::post('account/start-profile', [AccountController::class, 'startProfile']);

//Route::middleware('auth:sanctum')->group(function () {
Route::post('accounts', [AccountController::class, 'index']);

Route::post('account/create', [AccountController::class, 'create']);
Route::post('account/get-account', [AccountController::class, 'getAccount']);
Route::post('account/view', [AccountController::class, 'view']);
Route::post('account/delete', [AccountController::class, 'delete']);
Route::post('account/edit', [AccountController::class, 'edit']);
Route::post('account/delete-warning', [AccountController::class, 'deleteWarning']);
Route::post('account/make-active', [AccountController::class, 'makeActive']);
Route::post('account/clear-next-login', [AccountController::class, 'clearNextLogin']);
Route::post('account/set-category', [AccountController::class, 'setCategory']);
Route::post('accounts/fetch-accounts', [AccountController::class, 'fetchAccounts']);
Route::post('account/clear-profile', [AccountController::class, 'clearProfile']);
Route::post('accounts/get-2fa-code', [AccountController::class, 'get2faCode']);
Route::post('account/assign-fingerprint', [AccountController::class, 'assignFingerprint']);
Route::post('account/find-accounts', [AccountController::class, 'findAccounts']);
Route::post('account/attach-tag', [AccountController::class, 'attachTag']);
Route::post('account/detach-tag', [AccountController::class, 'detachTag']);
Route::post('account/attach-service', [AccountController::class, 'attachService']);
Route::post('account/detach-service', [AccountController::class, 'detachService']);
Route::post('account/reset-is-used', [AccountController::class, 'resetIsUsed']);

Route::post('leads', [LeadController::class, 'index']);
Route::post('lead/view', [LeadController::class, 'view']);
Route::post('lead/delete', [LeadController::class, 'delete']);
Route::post('lead/edit', [LeadController::class, 'edit']);
Route::post('lead/change-state', [LeadController::class, 'changeState']);
Route::post('lead/set-category', [LeadController::class, 'setCategory']);
Route::post('lead/import', [LeadController::class, 'import']);
Route::post('lead/get-statuses', [LeadController::class, 'getStatuses']);
Route::post('lead/export', [LeadController::class, 'export']);

Route::post('templates', [TemplateController::class, 'index']);
Route::post('template/delete', [TemplateController::class, 'delete']);
Route::post('template/view', [TemplateController::class, 'view']);
Route::post('template/create', [TemplateController::class, 'create']);
Route::post('template/update', [TemplateController::class, 'update']);
Route::post('template/upload-file', [TemplateController::class, 'uploadFile']);
Route::post('template/fetch-types', [TemplateController::class, 'fetchTypes']);
Route::post('template/get-template', [TemplateController::class, 'getTemplate']);
Route::post('template/attach-tag', [TemplateController::class, 'attachTag']);

Route::post('proxies', [ProxyController::class, 'index']);
Route::post('proxy/create', [ProxyController::class, 'create']);
Route::post('proxy/view', [ProxyController::class, 'view']);
Route::post('proxy/delete', [ProxyController::class, 'delete']);
Route::post('proxy/edit', [ProxyController::class, 'edit']);
Route::post('proxies/fetch-proxies', [ProxyController::class, 'fetchProxies']);

Route::post('threads', [ThreadController::class, 'index']);
Route::post('get-threads', [ThreadController::class, 'getThreads']);
Route::post('get-loom-threads', [ThreadController::class, 'getLoomThreads']);
Route::post('thread/view', [ThreadController::class, 'view']);
Route::post('thread/set-category', [ThreadController::class, 'setCategory']);

Route::post('messages', [MessageController::class, 'index']);

Route::post('commands', [CommandController::class, 'index']);
Route::post('command/create-custom-message', [CommandController::class, 'createCustomMessage']);
Route::post('command/create-custom-message-with-message_id', [CommandController::class, 'createCustomMessageWithMsgId']);
Route::post('command/create-get-directs', [CommandController::class, 'createGetDirects']);
Route::post('command/create-upload-loom', [CommandController::class, 'createUploadLoom']);
Route::post('command/get-types', [CommandController::class, 'getTypes']);
Route::post('command/get-statuses', [CommandController::class, 'getStatuses']);

Route::post('looms', [LoomController::class, 'index']);
Route::post('loom/delete', [LoomController::class, 'delete']);
Route::post('loom/view', [LoomController::class, 'view']);

Route::post('dashboard/dm-statistics', [DashboardController::class, 'getDailyDmStatistics']);
Route::post('dashboard/running-accounts', [DashboardController::class, 'getRunningAccounts']);

Route::post('spintaxes', [SpintaxController::class, 'index']);
Route::post('spintaxe/view', [SpintaxController::class, 'view']);
Route::post('spintaxe/create', [SpintaxController::class, 'create']);
Route::post('spintaxe/update', [SpintaxController::class, 'update']);
Route::post('spintax/delete', [SpintaxController::class, 'delete']);

Route::post('categories', [CategoryController::class, 'index']);
Route::post('categories/view', [CategoryController::class, 'view']);
Route::post('categories/create', [CategoryController::class, 'create']);
Route::post('categories/edit/{id}', [CategoryController::class, 'edit']);
Route::post('categories/delete', [CategoryController::class, 'delete']);

Route::post('tags', [TagController::class, 'index']);
Route::post('tik-tok-tags', [TagController::class, 'tikTokTags']);
Route::post('tags/create', [TagController::class, 'create']);
Route::post('tags/edit/{id}', [TagController::class, 'edit']);
Route::post('tags/delete', [TagController::class, 'delete']);
Route::post('tags/search', [TagController::class, 'search']);

Route::post('hashtags', [HashtagController::class, 'index']);
Route::post('hashtags/create', [HashtagController::class, 'create']);
Route::post('hashtags/edit/{id}', [HashtagController::class, 'edit']);
Route::post('hashtags/delete', [HashtagController::class, 'delete']);
Route::post('hashtags/search', [HashtagController::class, 'search']);


Route::post('lead-sources', [LeadSourceController::class, 'index']);
Route::post('lead-sources/create', [LeadSourceController::class, 'create']);
Route::post('lead-sources/edit/{id}', [LeadSourceController::class, 'edit']);
Route::post('lead-sources/delete', [LeadSourceController::class, 'delete']);
Route::post('lead-sources/search', [LeadSourceController::class, 'search']);

Route::post('dm-posts', [DmPostController::class, 'index']);
Route::post('dm-posts/create', [DmPostController::class, 'create']);
Route::post('dm-posts/edit/{id}', [DmPostController::class, 'edit']);
Route::post('dm-posts/delete', [DmPostController::class, 'delete']);
Route::post('dm-posts/search', [DmPostController::class, 'search']);

Route::post('profiles', [ProfileController::class, 'index']);
Route::post('profiles/delete', [ProfileController::class, 'delete']);
Route::post('profiles/create', [ProfileController::class, 'create']);
Route::post('profiles/make-and-assign-profiles', [ProfileController::class, 'makeAndAssignProfiles']);
Route::post('profiles/api/assign-to-account', [ProfileController::class, 'assignToAccountAPI']);
Route::post('profiles/edit', [ProfileController::class, 'edit']);

Route::post('clis', [CliController::class, 'index']);

Route::post('users/get-users-by-name', [UserController::class, 'getUsersByName']);

Route::post('colors', [ColorController::class, 'index']);
Route::post('colors/create', [ColorController::class, 'store']);
Route::post('colors/edit/{id}', [ColorController::class, 'update']);
Route::post('colors/delete', [ColorController::class, 'destroy']);


Route::post('orders', [OrderController::class, 'index']);
Route::post('orders/create', [OrderController::class, 'create']);
Route::post('order/delete', [OrderController::class, 'delete']);
Route::post('order/finish', [OrderController::class, 'finish']);
Route::post('order/fail', [OrderController::class, 'fail']);
Route::post('order/reset', [OrderController::class, 'reset']);
Route::post('order/change-processing-to-free', [OrderController::class, 'changeProcessingToFree']);
Route::post('order/get-actions', [OrderController::class, 'getActions']);
Route::post('orders/report', [OrderController::class, 'report']);
Route::post('api/v3', [OrderController::class, 'v3']);
Route::post('api/telegram-group-sender', [OrderController::class, 'telegramGroupSender']);
Route::post('api/v4', [OrderController::class, 'v4']);
Route::post('api/comment-and-reply', [OrderController::class, 'commentAndReply']);


Route::post('settings', [SettingController::class, 'index']);
Route::post('setting/update', [SettingController::class, 'update']);


Route::prefix('processes')->group(function () {
    Route::get('/', [ProcessController::class, 'index']);
    Route::get('/servers/', [ProcessController::class, 'getServers']);
    Route::get('/initial-data', [ProcessController::class, 'getInitialData']);
    Route::post('/update', [ProcessController::class, 'update']);
    Route::post('/delete', [ProcessController::class, 'delete']);
    Route::post('/toggle-process', [ProcessController::class, 'toggleProcess']);
    Route::post('/set-workflow', [ProcessController::class, 'setWorkflow']);
    Route::post('/set-status', [ProcessController::class, 'setStatus']);
    Route::post('/check', [ProcessController::class, 'check']);
    Route::post('/set-status-by-servers', [ProcessController::class, 'setStatusByServers']);
    Route::post('/set-workflow-by-servers', [ProcessController::class, 'setWorkflowByServers']);
    Route::post('/delete-by-servers', [ProcessController::class, 'deleteByServers']);
});

Route::post('services', [ServiceController::class, 'index']);
Route::post('services/create', [ServiceController::class, 'create']);
Route::post('services/search', [ServiceController::class, 'search']);
Route::post('services/update', [ServiceController::class, 'update']);
Route::post('service/delete', [ServiceController::class, 'delete']);


Route::post('workflows', [WorkflowController::class, 'index']);
Route::post('workflows/create', [WorkflowController::class, 'create']);
Route::post('workflows/update', [WorkflowController::class, 'update']);
Route::post('workflow/delete', [WorkflowController::class, 'delete']);

Route::post('modules', [ModuleController::class, 'index']);
Route::post('modules/search', [ModuleController::class, 'search']);
Route::post('modules/create', [ModuleController::class, 'create']);
Route::post('modules/update', [ModuleController::class, 'update']);
Route::post('module/delete', [ModuleController::class, 'delete']);

Route::post('account-specs', [AccountSpecController::class, 'index']);

Route::prefix('tiktok-links')->group(function () {
    Route::post('/', [TikTokLinkController::class, 'index']);
    Route::post('/create', [TikTokLinkController::class, 'store']);
    Route::delete('/{id}', [TikTokLinkController::class, 'destroy']);
    Route::put('/{id}', [TikTokLinkController::class, 'update']);
    Route::post('/generate-images', [TikTokLinkController::class, 'generateImages']);
    Route::post('/download-images', [TikTokLinkController::class, 'downloadImages']);
    Route::post('/force-run', [TikTokLinkController::class, 'forceRun']);
});

Route::post('tik-tok-tags/store', [TikTokTagController::class, 'index']);
Route::delete('tik-tok-tags/{id}', [TikTokTagController::class, 'destroy']);


Route::post('account/upload-post-connect', [AccountController::class, 'uploadPostConnect']);
Route::post('account/upload-post-disconnect', [AccountController::class, 'uploadPostDisconnect']);
Route::post('account/toggle-upload-post', [AccountController::class, 'toggleUploadPost']);
Route::post('account/reset-upload-post-status', [AccountController::class, 'resetUploadPostStatus']);

Route::post('duo-workflow/start', [DuoWorkFlowController::class, 'start']);
Route::post('duo-workflow/get-url', [DuoWorkFlowController::class, 'getUrl']);
Route::post('duo-workflow/get-action-count', [DuoWorkFlowController::class, 'getActionCount']);
Route::post('duo-workflow/group-click', [DuoWorkFlowController::class, 'groupClick']);
Route::post('duo-workflow/change-account', [DuoWorkFlowController::class, 'changeAccount']);
Route::post('/duo-workflow/fail', [DuoWorkFlowController::class, 'fail']);
Route::post('/test-case', function () {
    Log::channel('api')->info(request()->all());
});

//});
