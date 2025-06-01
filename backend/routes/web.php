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

//Tiktok Offer - Cold DM (TEST)	cold dm	👋 {Hey guys|Hey there|Hi|Hello|Greetings}, {Your store popped up on my feed|Your shop caught my eye|I came across your store|I stumbled upon your business|I noticed your store} and I thought I'd reach out because {I was very impressed by your products|I was blown away by your product lineup|your products really stood out to me|I love the products you're offering|your items look fantastic} 🤩.\n\n{Idk if you're familiar with TikTok Shop|Not sure if you’ve heard of TikTok Shop|You might have heard of TikTok Shop}, but {it's the revolution of the decade for ecomm owners|it's the next big thing in e-commerce|it's revolutionizing the ecomm world|it's disrupting how ecomm works}. {We run TT Shop systems for brands like yours|We help stores like yours generate $90k+ in new monthly sales|We manage TikTok Shop systems for businesses like yours} and {make it \\"unfairly easy\\" to get $90k+ in new monthly revenue with ZERO acquisition costs or ad spend|make it super easy to pull in $90k+ monthly without any ad costs|bring in $90k+ in new sales without spending a dime on ads}.\n\nIt's {quite brilliant|a genius system|incredibly effective|honestly pretty smart} 😋. I've {gone ahead and filmed you a personal Loom|recorded a quick Loom video|made a personalized Loom video|filmed a short video|put together a Loom just for you} going over why {your brand can be a huge hit on there|your store could succeed on there|your brand has huge potential on TikTok Shop|your store would crush it on there} – {mind if I send it over?|would it be cool if I shared it with you?|can I send it your way?|let me know if you'd like me to share it with you|should I send it over for you?}\n\n{Cheers|Best|Talk soon|All the best|Take care},\n{Edward|Ed|Eddie|Eddy}	\N	2024-10-12 16:30:38	2024-10-12 16:30:38
//2	FUP1 TT SHOP	first dm follow up	{Just checking in|Following up|Just wanted to follow up|Checking in real quick|Quick follow-up} to see if {you had a chance to see my previous message|you got a chance to check out my last message|you’ve had a moment to review my last message|you saw my last message|you had time to review my last note} about {using TikTok Shop to boost your revenue|leveraging TikTok Shop to increase your sales|utilizing TikTok Shop to grow your business|how TikTok Shop can skyrocket your revenue|the potential of TikTok Shop to raise your revenue}.\n\n{There’s no acquisition cost for new customers|You won’t have to spend anything to acquire new customers|There’s zero cost for customer acquisition|No acquisition costs whatsoever for new customers|You won’t spend a dime on acquiring customers}. {You don’t need any ad spend at all|You won’t need any ad spend to make this work|Not a penny of ad spend is required|You don’t need any ads to get results|No need for ad spend to generate sales}. {When the sales roll in, it’s pure profit|Any sales you make are 100% profit|Every sale is straight profit|Each sale is pure profit|It’s all profit when sales come in}.\n\n{It’s a game changer for qualifying stores|Stores that qualify will see game-changing results|It’s a total game changer for the right stores|Stores that qualify can see massive changes|Qualifying stores will experience transformative growth}, and {brands jumping in now will have insane valuations in the future|businesses that get in early will have huge future valuations|early adopters will see massive future valuations|brands that act fast will gain crazy valuations down the line|brands that ride the wave now will see wild valuations later}. I’ll {explain everything in the Loom|break it all down in the Loom video|walk you through it all in the Loom video|cover all the details in the Loom video|explain it fully in the Loom video} for you – {it’s a quick watch|it’ll only take a few minutes|it won’t take long|it’s a super short video|it’s a fast watch}, but {probably the highest ROI thing you can do for your business this year|likely the most ROI-boosting move you can make this year|could be the best ROI move you make for your business this year|might just be the smartest thing you do for ROI this year|likely the most impactful move for your ROI this year}.	\N	2024-10-13 18:11:46	2024-10-13 18:11:46
//3	FUP2 TT SHOP	second dm follow up	{Hey guys|Hey there|Hi|Hello|Greetings}, {I know your inbox is probably flooded|I’m sure your inbox is packed|I bet you get tons of messages|I know you’re probably swamped with messages|I bet your inbox is busy}, but I wanted to {make sure my message didn’t get lost in the shuffle|ensure my message didn’t get buried|check that my last message didn’t slip through the cracks|make sure you didn’t miss my previous note|see if my message didn’t get lost}.\n\n{I really think the video I recorded for you about TikTok Shop could skyrocket your business|The video I filmed on TikTok Shop could seriously boost your business|I believe the Loom I made about TT Shop could really grow your business|That video I made could be the game-changer for your store|I think the video I created could really take your business to the next level}. Again, {there's no acquisition cost involved|there’s zero cost for acquiring customers|you won’t need to spend anything on customer acquisition|no customer acquisition costs at all|you won’t pay a cent for acquiring new customers} — {imagine an ad platform where you only pay AFTER you get a sale|picture a platform where you only pay after a sale is made|think of an ad platform where you only pay once you’ve made a sale|it’s like an ad platform where you pay only after you’ve secured a sale|it’s a system where payment only happens once a sale is made}, and {that’s capped at a fraction of the sale price|the fee is only a small percentage of the sale price|the cost is just a fraction of what you make on each sale|it’s capped at a small portion of the sale value|the cost is just a tiny part of the sale amount}. {That’s TikTok Shop in a nutshell when you’ve got the right systems in place|That’s the essence of TikTok Shop when the right systems are set up|That’s how TikTok Shop works when you use the right systems|With the right systems, that’s what TikTok Shop is|That’s what TikTok Shop can do with the right systems behind it}.\n\n{I’d love to send the Loom over to the owner of your brand|I’d be happy to share the Loom with the owner of your business|I’d like to send that Loom video to the brand owner|I’m ready to send that Loom to the business owner|I’d love to pass that Loom video to the brand owner}. {Do you think they’d be interested?|You think they’d be interested in seeing it?|Would they be open to checking it out?|You think the owner would want to see it?|Do you reckon they’d want to have a look?}	\N	2024-10-13 18:12:06	2024-10-13 18:12:06
//4	FUP3 TT SHOP	third dm follow up	{Hey|Hi|Hello|Yo} {just checking|just wanted to check|making sure|double-checking} {if you saw|whether you noticed|if you got|if you received} {my messages|the message I sent|my previous texts|my earlier message}.	\N	2024-10-14 17:13:19	2024-10-14 17:13:19
//\.
//aea5145d4c7469bc:RNW78Fm5@res.proxy-seller.com:10000
Route::get('/', function () {
    \App\Models\Log::query()->delete();

    dd('shod');

//
//    $clis = \App\Models\Cli::query()
//        ->where('log', 'like', '%Selected username%')
//        ->get()
//        ->pluck('log')
//        ->toArray();
//
//    dd($clis);

//    // Fetch all active accounts
//    $accounts = Account::query()->where('instagram_state', 'active')->pluck('username');
//
//// Define the file path where the CSV will be saved
//    $outputPath = storage_path('app/activeaccounts.csv');
//
//// Create the CSV writer and specify the output file path
//    $csv = \League\Csv\Writer::createFromPath($outputPath, 'w+');
//
//// Add the header to the CSV file
//    $csv->insertOne(['Username']);
//
//// Insert each active account's username into the CSV
//    foreach ($accounts as $username) {
//        $csv->insertOne([$username]);
//    }

// Inform the user

//    dd('shod');

//    Account::query()->update([
//        'has_enough_posts'=>1
//    ]);
//
//    $accs = Account::query()->where('has_enough_posts', 0)->count();
//
//    dd($accs);

//    Profile::query()->where('proxy_id', null)->get()
//        ->each(function ($profile) {
//            $profile->proxy_id = Proxy::getWithFewestProfiles()->id;
//            $profile->save();
//            dump($profile->proxy_id);
//        });
//
//    dd(Profile::query()->where('proxy_id', null)->count());
//    Setting::setValue('can_generate_lead_by_followers', false);


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



