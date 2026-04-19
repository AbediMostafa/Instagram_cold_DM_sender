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
use App\Models\Order;
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
use \App\Models\Template;
use \App\Models\Lead;
use \App\Models\Account;
use \App\Models\Tag;
use \App\Models\Proxy;
use \App\Models\Profile;

Route::get('/', function () {

});
Route::get('/test', function () {
    dd(
        \App\Models\Ip::query()->get()->pluck('ip')->toArray()
    );

});


//
//$order->completed_count = $order->actions_count;
//$order->status = 'In progress';
//$order->save();
//$order->actions()->whereNull('account_id')->update(['status'=>'free']);
//
//dd($order);


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
Route::post('api/v3', [OrderController::class, 'v3']);
Route::post('api/telegram-group-sender', [OrderController::class, 'telegramGroupSender']);
Route::post('api/v4', [OrderController::class, 'v4']);


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

//});
