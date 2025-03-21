<?php

use App\Classes\AdspowerProfileMaker;
use App\Classes\AdsPowerProfileUpdateProxy;
use App\Classes\ProfileDelete;
use App\Classes\ProfileMaker;
use App\Classes\ProfileMakerV2;
use App\Classes\ProfileRequest;
use App\Models\Account;
use App\Models\Command;
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


Route::get('/', function () {
//    $account = Account::query()->where('username', 'keshavarz_fm7')->first()->category_id;
//
//    dd($account);

//    $url = "http://local.adspower.net:50325/api/v1/user/list";
//
//    $response = Http::withoutVerifying()->get($url);
//
//    dd($response->json());


//    $accounts = DB::connection('old_pgsql')
//        ->table('accounts')
//        ->get()
//        ->each(function ($account) {
//            Account::query()->where('username', $account->username)->doesntExist()&&
//            Account::query()->create([
//                'secret_key'=>$account->secret_key,
//                'username'=>$account->username,
//                'email'=>$account->email,
//                'password'=>$account->password,
//                'name'=>$account->name,
//                'bio'=>$account->bio,
//                'color_id'=>$account->color_id,
//                'avatar_changed'=>$account->avatar_changed,
//                'username_changed'=>$account->username_changed,
//                'initial_posts_deleted'=>$account->initial_posts_deleted,
//                'is_public'=>$account->is_public,
//                'web_session'=>$account->web_session,
//                'created_at'=>$account->created_at,
//            ]);
//        })
//    ;
//
//    dd('$accounts');
});

Route::get('/activate-accounts', function () {
//    Account::all()->each(function ($account) {
//        $account->makeActive();
//    });
//    dd('shod');


//
});


Route::post('login', [AuthController::class, 'login']);
Route::post('sign-out', [AuthController::class, 'signOut']);
Route::post('lead/api/export', [LeadController::class, 'exportApi']);
Route::post('categories/get-categories', [CategoryController::class, 'getCategories']);
Route::post('app-config', [AppConfigController::class, 'index']);
Route::post('account/get-proxy-api', [AccountController::class, 'getProxyApi']);
Route::post('account/change-profile-proxy-to-residential', [AccountController::class, 'changeProfileProxyToResidentialApi']);
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


