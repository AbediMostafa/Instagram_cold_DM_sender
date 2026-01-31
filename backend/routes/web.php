<?php

use App\Classes\AdspowerProfileMaker;
use App\Classes\AdsPowerProfileUpdateProxy;
use App\Classes\Fingerprint;
use App\Classes\ProfileDelete;
use App\Classes\ProfileMaker;
use App\Classes\ProfileMakerV2;
use App\Classes\ProfileRequest;
use App\Models\Account;
use App\Models\CharityLead;
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
use \App\Http\Controllers\OrderController;
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
use \App\Models\EnrichedLead;
use \App\Models\Order;
use \App\Models\OrderComment;
use \App\Http\Controllers\SettingController;
use \App\Http\Controllers\ProcessController;
use App\Http\Controllers\ServiceController;
use \App\Http\Controllers\WorkflowController;
use App\Http\Controllers\ModuleController;
use \Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Redis;
use PhpOffice\PhpSpreadsheet\IOFactory;
use App\Http\Controllers\AccountSpecController;


Route::get('/', function () {


//    $account = Account::query()->find(19024);
//
//    dd($account->username_changed);

//   $accounts =  Account::query()
//       ->where('instagram_state', '!=', 'active')
//       ->get()
//        ->each(function(Account $account){
//            $account->makeActive();
//            runPythonProcess('new.py', $account->id);
//        });
});

Route::get('/add-comment', function () {
});
Route::get('/get-instagram-leads', function () {
    $leads = \App\Models\CharityLead::query()

//        ->whereNotNull('linkedin')
        ->whereNotNull('instagram')
        ->count();

    dd($leads);
});
Route::get('/update-charities', function () {
    $s = \App\Models\CharityLead::query()
        ->where('id', '>', 280000)
        ->update([
            'is_used' => 0
        ]);

    dd($s);
});
Route::get('/import_charity_leads_test', function () {
    $path = storage_path('app/charity leads/crunchbase_companies');
    $files = glob($path . '/*.csv');

    foreach ($files as $file) {
        $handle = fopen($file, 'r');
        if (!$handle) continue;

        $headers = fgetcsv($handle);

        $batch = [];
        $count = 0;

        while (($row = fgetcsv($handle)) !== false) {

            $data = array_combine($headers, $row);

            $insertingData = [
                'data' => json_encode($data),
                'company_name' => $data["name"],
                'phone_number' => $data["phone_number"],
                'website' => $data["website"],
                'email' => $data["contact_email"],
                'linkedin' => $data["linkedin"],
                'lead_type' => 'crunchbase_companies_leads',
                'is_used' => 0
            ];

            try {
                \App\Models\CharityLead::query()->create($insertingData);
                $count += 1;
            } catch (Throwable $e) {
                dump($e->getMessage());
                dump($insertingData);
            }
        }

        dump("✅ Imported {$count} rows from" . basename($file));
    }
});
Route::get('/import_charity_leads', function () {
    $path = storage_path('app/charity leads/crunchbase_companies');
    $files = glob($path . '/*.csv');

    foreach ($files as $file) {
        $handle = fopen($file, 'r');
        if (!$handle) continue;

        $headers = fgetcsv($handle);

        $batch = [];
        $count = 0;

        while (($row = fgetcsv($handle)) !== false) {

            $data = array_combine($headers, $row);

            $linkedin = $data['linkedin'];

            $batch[] = [
                'data' => json_encode($data),
                'company_name' => $data["name"],
                'phone_number' => $data["phone_number"],
                'website' => $data["website"],
                'email' => $data["contact_email"],
                'linkedin' => $data["linkedin"],
                'lead_type' => 'crunchbase_companies_leads'
            ];

            // Insert every 1000 rows for efficiency
            if (count($batch) >= 1000) {
                DB::table('charity_leads')->insert($batch);
                $count += count($batch);
                $batch = [];
            }
        }

        if (!empty($batch)) {
            DB::table('charity_leads')->insert($batch);
            $count += count($batch);
        }

        dump("✅ Imported {$count} rows from" . basename($file));
    }
});
Route::get('/make-username', function () {
    $keywords = ['it', 'software', 'tech', 'company', 'ai', 'style', 'new'];
    $decorators = ['_', '.', '__', '___', '._', '_.', '._._.', '_._', '._.'];
    $usernames = [];
    $nums = [1404, 2025, 2024, 2023, 2000, 1400, 1401, 2002,];
    while (count($usernames) < 500) {
        // تصمیم: یک کلمه یا دوتا
        $count = rand(1, 2);
        $chosen = [];

        // انتخاب تصادفی از آرایه
        $keys = array_rand($keywords, $count);
        if ($count === 1) {
            $chosen[] = $keywords[$keys];
        } else {
            foreach ($keys as $k) {
                $chosen[] = $keywords[$k];
            }
        }

        $wordPart = implode('', $chosen); // ترکیب کلمات
        $dec = $decorators[array_rand($decorators)];
        $num = $nums[array_rand($nums)];

        // اجزای ممکن
        $parts = [$wordPart, (string)$num, $dec];

        // جابجایی رندوم
        shuffle($parts);

        $username = implode('', $parts);

        // 🔎 فیلتر قوانین اینستاگرام:
        // 1. طول < 30
        // 2. شروع نشدن با . یا _
        // 3. تمام نشدن با . یا _
        if (
            strlen($username) < 30 &&
            !in_array($username, $usernames) &&
            !preg_match('/^[_\.]/', $username) &&   // شروع نشه با . یا _
            !preg_match('/[_\.]$/', $username)      // تموم نشه با . یا _
        ) {
            $usernames[] = $username;
        }

        Template::query()
            ->where('type', 'username')
            ->where('text', $username)
            ->doesntExist()
        &&
        Template::query()
            ->create([
                'text' => $username,
                'type' => 'username'
            ]);
    }
    dd($usernames);
});
Route::get('/activate-accounts', function () {
    Account::all()->each(function ($account) {
        $account->makeActive();
    });
    dd('shod');
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
Route::post('order/change-processing-to-free', [OrderController::class, 'changProcessingCommentsToFree']);
Route::post('order/there-is-no-comment', [OrderController::class, 'thereIsNoComment']);
Route::post('api/v3', [OrderController::class, 'v3']);
Route::post('api/telegram-group-sender', [OrderController::class, 'telegramGroupSender']);


Route::post('settings', [SettingController::class, 'index']);
Route::post('setting/update', [SettingController::class, 'update']);


Route::post('processes', [ProcessController::class, 'index']);
Route::post('processes/check', [ProcessController::class, 'check']);
Route::post('processes/update', [ProcessController::class, 'update']);
Route::post('processes/delete', [ProcessController::class, 'delete']);
Route::post('processes/toggle-process', [ProcessController::class, 'toggleProcess']);
Route::post('processes/get-initial-data', [ProcessController::class, 'getInitialData']);
Route::post('processes/set-workflow', [ProcessController::class, 'setWorkflow']);
Route::post('processes/set-status', [ProcessController::class, 'setStatus']);

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

//});
