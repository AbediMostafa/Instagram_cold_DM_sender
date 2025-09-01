<?php

use App\Classes\AdspowerProfileMaker;
use App\Classes\AdsPowerProfileUpdateProxy;
use App\Classes\Fingerprint;
use App\Classes\ProfileDelete;
use App\Classes\ProfileMaker;
use App\Classes\ProfileMakerV2;
use App\Classes\ProfileRequest;
use App\Models\Account;
use App\Models\Command;
use App\Models\DmPost;
use App\Models\Message;
use App\Models\Profile;
use App\Models\Proxy;
use App\Models\Setting;
use App\Models\Spintax;
use App\Models\Thread;
use App\Models\User;
use Carbon\Carbon;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Route;
use \App\Http\Controllers\AccountController;
use \App\Http\Controllers\AppConfigController;
use \App\Http\Controllers\TemplateController;
use \App\Http\Controllers\CliController;
use \App\Http\Controllers\LeadController;
use \App\Http\Controllers\ProxyController;
use \App\Http\Controllers\ThreadController;
use \App\Http\Controllers\MessageController;
use \App\Http\Controllers\CommandController;
use \App\Http\Controllers\LoomController;
use \App\Http\Controllers\DashboardController;
use \App\Http\Controllers\SpintaxController;
use \App\Http\Controllers\AuthController;
use \App\Http\Controllers\CategoryController;
use \App\Http\Controllers\TagController;
use \App\Http\Controllers\UserController;
use \App\Http\Controllers\ProfileController;
use \Illuminate\Support\Facades\Http;
use \App\Http\Controllers\HashtagController;
use App\Http\Controllers\LeadSourceController;
use App\Http\Controllers\DmPostController;
use \App\Models\Tag;
use JetBrains\PhpStorm\ArrayShape;
use Morilog\Jalali\Jalalian;
use Symfony\Component\HttpKernel\Exception\HttpException;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use Dotenv\Dotenv;
use \App\Classes\ProfileUpdateProxy;
use \App\Http\Controllers\ColorController;
use \App\Models\Hashtag;
use \App\Classes\ProfileGetProxy;
use \App\Models\Category;
use \App\Models\Template;
use \App\Models\LeadSource;
use \App\Models\Lead;
use \App\Models\Role;

//پس باید یوزرنیم اینستاگرام واقعی‌پسند بسازم که:
//
//فقط حروف انگلیسی و عدد باشه (به‌همراه . یا _)
//
//زیر ۳۰ کاراکتر
//
//شامل کلمات mobleman، choob، یا zendegi باشه
// یا ترجمه انگلیسی اونها باشه

// میتونی از هر مقدار ترکیب _ مانند __ یا ___ یا ._._. یا هر نوعی از ترکیبش بین یوزرنیم ها استفاده کنی
//یونیک و بامسما باشه
//حاصل رو توی یه آرایه پی اچ پی به من بده

Route::get('/', function () {
//
//    Account::query()->where('id','<', 4004)
//        ->update([
//            'is_used'=>1
//        ]);
//    $accounts = Account::query()->orderBy('id')->get()->pluck('is_used','id')->toArray();
//    dd($accounts);
//    Account::query()->where('id','!=',24)->update([
//        'api_is_used'=>0
//    ]);
////
//    private.residential.proxyrack.net:10000:mostafaaabedi-country-DE:EHRMBAG-FUVSHPY-STBMCL5-FVPSB1F-FZZ1GQG-40OBXSB-KDRAQ6S
//    private.residential.proxyrack.net:10001:mostafaaabedi-country-DE:EHRMBAG-FUVSHPY-STBMCL5-FVPSB1F-FZZ1GQG-40OBXSB-KDRAQ6S
//    private.residential.proxyrack.net:10002:mostafaaabedi-country-DE:EHRMBAG-FUVSHPY-STBMCL5-FVPSB1F-FZZ1GQG-40OBXSB-KDRAQ6S
//    private.residential.proxyrack.net:10003:mostafaaabedi-country-DE:EHRMBAG-FUVSHPY-STBMCL5-FVPSB1F-FZZ1GQG-40OBXSB-KDRAQ6S
//    private.residential.proxyrack.net:10004:mostafaaabedi-country-DE:EHRMBAG-FUVSHPY-STBMCL5-FVPSB1F-FZZ1GQG-40OBXSB-KDRAQ6S


});

Route::get('/make-username', function () {
    $usernames = [
        'mobleman__choob__life',
        'choob___mobleman.life',
        'life__mobleman__choob',
        'choob__zendegi__decor',
        'wood__mobleman___life',
        'living__choob__style',
        'furniture__choob__life',
        'choob__wood__living__',
        'mobleman..choob__life',
        'choob__zendegi..life',
        'life___choob__decor',
        'decor__mobleman__choob',
        'wood__life__mobleman',
        'living__choob___home',
        'mobleman__wood__decor',
        'choob__life__style__',
        'style__choob__mobleman',
        'life__wood__furniture',
        'mobleman__decor__life',
        'wood__choob__living__',
        'choob__life__zendegi',
        'zendegi__choob__life',
        'mobleman__choob__2025',
        'choob__living__2025',
        'wood__life__design__',
        'life__choob__decor__',
        'choob__mobleman__style',
        'living__choob__design',
        'design__wood__mobleman',
        'mobleman__life__choob',
        'choob__mobleman__2024',
        'style__life__choob__',
        'choob__living__decor',
        'decor__choob__living',
        'wood__choob__mobleman',
        'life__choob__living__',
        'choob__style__mobleman',
        'mobleman__wood__life__',
        'choob__furniture__life',
        'life__choob__furniture',
        'choob__mobleman__design',
        'design__choob__life',
        'life__wood__choob__',
        'choob__mobleman__living',
        'living__mobleman__choob',
        'choob__decor__life__',
        'mobleman__choob__living',
        'wood__choob__style__',
        'life__choob__home__',
        'choob__mobleman__home',
        'mobleman__choob__home',
        'home__choob__life__',
        'style__choob__living',
        'choob__mobleman__trend',
        'trend__choob__life__',
        'choob__mobleman__modern',
        'modern__choob__life',
        'choob__life__classic',
        'classic__choob__life__',
        'mobleman__choob__classic',
        'choob__life__design__',
        'life__choob__modern',
        'modern__life__choob',
        'choob__mobleman__living_',
        'mobleman__choob__trendy',
        'choob__furniture__decor',
        'decor__choob__mobleman',
        'mobleman__choob__world',
        'world__choob__life__',
        'choob__mobleman__dream',
        'dream__choob__life',
        'life__choob__dream__',
        'choob__mobleman__wood',
        'wood__choob__life',
        'choob__mobleman__zone',
        'zone__choob__life__',
        'choob__style__wood__',
        'style__choob__home',
        'home__choob__living',
        'choob__mobleman__house',
        'house__choob__life__',
        'choob__mobleman__villa',
        'villa__choob__life__',
        'choob__mobleman__trend_',
        'choob__life__wood__',
        'choob__mobleman__design_',
        'choob__life__dream_',
        'choob__wood__style__',
        'style__wood__life',
        'choob__wood__decor__',
        'decor__wood__life__',
        'mobleman__wood__dream',
        'dream__wood__life__',
        'choob__living__trend__',
        'trend__life__choob__',
        'choob__mobleman__classic_',
        'classic__mobleman__choob',
        'choob__mobleman__art',
        'art__choob__life',
        'life__choob__art__',
        'choob__mobleman__2026',
        'choob__mobleman__designs',
        'choob__design__life__',
        'design__choob__home',
        'home__choob__decor',
        'choob__mobleman__decor_',
        'mobleman__choob__living_',
        'living__choob__dream',
        'dream__choob__home',
        'choob__life__decor_',
        'choob__mobleman__ideas',
        'ideas__choob__life__',
        'choob__mobleman__vision',
        'vision__choob__life__',
        'choob__style__dream',
        'dream__choob__style__',
        'choob__mobleman__modern_',
        'mobleman__choob__future',
        'future__choob__life',
        'choob__mobleman__gold',
        'gold__choob__life',
        'life__choob__shine__',
        'shine__choob__life',
        'choob__mobleman__elite',
        'elite__choob__life__',
        'choob__mobleman__designs_',
        'choob__style__classic',
        'classic__style__choob',
        'choob__mobleman__prime',
        'prime__choob__life__',
        'choob__wood__prime__',
        'prime__wood__life',
        'choob__mobleman__art_',
        'choob__life__unique',
        'unique__choob__life__',
        'choob__wood__unique',
        'choob__mobleman__decor__',
        'choob__mobleman__space',
        'space__choob__life',
        'choob__mobleman__spot',
        'spot__choob__life',
        'choob__style__spot__',
        'choob__wood__trend__',
        'choob__mobleman__best',
        'best__choob__life__',
        'choob__life__trend__',
        'trend__choob__living',
        'choob__wood__living_',
        'living__wood__choob__',
        'choob__decor__wood__',
        'choob__mobleman__decorx',
        'choob__mobleman__style_',
        'choob__life__artistic',
        'artistic__choob__life__',
        'choob__mobleman__house_',
        'house__mobleman__choob',
        'choob__mobleman__villa_',
        'choob__mobleman__zone_',
        'zone__mobleman__choob',
        'choob__mobleman__ideas_',
        'choob__mobleman__dream_',
        'choob__mobleman__modern__',
        'choob__mobleman__classic__',
        'choob__mobleman__future_',
        'choob__mobleman__gold_',
        'choob__mobleman__shine_',
        'choob__mobleman__prime_',
        'choob__mobleman__vision_',
        'choob__mobleman__spot_',
        'choob__mobleman__world_',
        'choob__mobleman__trend__',
        'choob__mobleman__dream__',
        'choob__mobleman__zone__',
        'choob__mobleman__artistic',
        'choob__mobleman__style__',
        'choob__mobleman__elite_',
        'choob__mobleman__decorx_',
        'choob__mobleman__unique_',
        'choob__mobleman__classic_',
        'choob__mobleman__modernx',
        'choob__mobleman__trendx',
        'choob__mobleman__decor__x',
        'choob__mobleman__life__x',
        'choob__mobleman__woodx',
        'choob__mobleman__dreamx',
        'choob__mobleman__zonex',
        'choob__mobleman__futurex',
        'choob__mobleman__shinex',
        'choob__mobleman__primex',
        'choob__mobleman__visionx',
        'choob__mobleman__spotx',
        'choob__mobleman__goldx',
        'choob__mobleman__artx',
        'choob__mobleman__bestx',
        'choob__mobleman__elitex',
        'choob__mobleman__housex',
        'choob__mobleman__villax',
        'choob__mobleman__zonex',
        'choob__mobleman__ideasx',
        'choob__mobleman__dreamxx',
        'choob__mobleman__trendxx',
        'choob__mobleman__stylexx',
        'choob__mobleman__modernxx',
        'choob__mobleman__decorxx',
        'choob__mobleman__classicxx',
        'choob__mobleman__futurexx',
        'choob__mobleman__primexx',
        'choob__mobleman__visionxx',
        'choob__mobleman__spotxx',
        'choob__mobleman__goldxx',
        'choob__mobleman__elitexx',
        'choob__mobleman__artxx',
        'choob__mobleman__bestxx',
        'choob__mobleman__zonexx',
        'choob__mobleman__dreamz',
        'choob__mobleman__trendz',
        'choob__mobleman__stylez',
        'choob__mobleman__modernz',
        'choob__mobleman__decorz',
        'choob__mobleman__classicz',
        'choob__mobleman__futurez',
        'choob__mobleman__primez',
        'choob__mobleman__visionz',
        'choob__mobleman__spotz',
        'choob__mobleman__goldz',
        'choob__mobleman__elitez',
        'choob__mobleman__artz',
        'choob__mobleman__bestz',
        'choob__mobleman__zonez',
        'choob__mobleman__lifez',
        'choob__mobleman__woodz',
        'choob__mobleman__dreamzz',
        'choob__mobleman__trendzz',
        'choob__mobleman__stylezz',
        'choob__mobleman__modernzz',
        'choob__mobleman__decorzz',
        'choob__mobleman__classiczz',
        'choob__mobleman__futurezz',
        'choob__mobleman__primezz',
        'choob__mobleman__visionzz',
        'choob__mobleman__spotzz',
        'choob__mobleman__goldzz',
        'choob__mobleman__elitezz',
        'choob__mobleman__artzz',
        'choob__mobleman__bestzz',
        'choob__mobleman__zonezz',
        'choob__mobleman__housezz',
        'choob__mobleman__villazz',
        'choob__mobleman__zonexzz',
        'choob__mobleman__lifezz',
        'choob__mobleman__woodzz',
        'choob__mobleman__dream_zz',
        'choob__mobleman__trend_zz',
        'choob__mobleman__style_zz',
        'choob__mobleman__modern_zz',
        'choob__mobleman__decor_zz',
        'choob__mobleman__classic_zz',
        'choob__mobleman__future_zz',
        'choob__mobleman__prime_zz',
        'choob__mobleman__vision_zz',
        'choob__mobleman__spot_zz',
        'choob__mobleman__gold_zz',
        'choob__mobleman__elite_zz',
        'choob__mobleman__art_zz',
        'choob__mobleman__best_zz',
        'choob__mobleman__zone_zz'
    ];
    foreach ($usernames as $username) {

        Template::query()
            ->where('type','username')
            ->where('text',$username)
            ->doesntExist()
            &&
        Template::query()
            ->create([
                'text' => $username,
                'type'=>'username'
            ]);
    }
});

Route::get('/activate-accounts', function () {
    Account::all()->each(function ($account) {
        $account->makeActive();
    });
    dd('shod');


//
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
Route::post('template/fetch-colors', [TemplateController::class, 'fetchColors']);

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
//});

Route::post('hidemyacc/create', function () {


    abort_if(r('user') !== 'info@teamair.life', 401);
    $proxy = json_encode([
        'host' => 'x473.fxdx.in',
        'port' => 14006,
        'mode' => 'socks5',
        'username' => 'usproxy273917',
        'password' => 'npCLeFIDxu5c',
    ]);

    $data = [
        'os' => r('os', 'win'),
        'name' => r('profile_name'),
        'folder' => r('folder', '67f7e6441a84c4c56660b546'),
        'notes' => r('notes', ''),
        'browser' => r('browser', 'chrome'),
        'proxy' => $proxy
    ];

    $response = Http::asForm()->post('http://127.0.0.1:2268/profiles', $data);


    return $response->json();
});



