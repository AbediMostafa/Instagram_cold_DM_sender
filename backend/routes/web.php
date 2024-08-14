<?php

use App\Models\Account;
use App\Models\Command;
use App\Models\Message;
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


Route::get('/', function () {

    $clis = Account::query()->find(466)
        ->clis;

    dd($clis[637]);

});

//function exportTables()
//{
//    Storage::put('accounts.json', DB::table('accounts')->get()->toJson());
//    Storage::put('leads.json', DB::table('leads')->get()->toJson());
//    Storage::put('templates.json', DB::table('templates')->get()->toJson());
//    Storage::put('accountTemplates.json', DB::table('account_template')->get());
//    Storage::put('clis.json', DB::table('clis')->get()->toJson());
//    Storage::put('commands.json', DB::table('commands')->get()->toJson());
//    Storage::put('leadHistories.json', DB::table('lead_histories')->get()->toJson());
//    Storage::put('logs.json', DB::table('logs')->get()->toJson());
//    Storage::put('messages.json', DB::table('messages')->get()->toJson());
//    Storage::put('threads.json', DB::table('threads')->get()->toJson());
//    Storage::put('dms.json', DB::table('dms')->get()->toJson());
//    Storage::put('proxies.json', DB::table('proxies')->get()->toJson());
//
//    dd('shod');
//}

Route::post('/test', function () {
    return 'salam';
});

Route::post('app-config', [AppConfigController::class, 'index']);
Route::post('accounts', [AccountController::class, 'index']);
Route::post('account/create', [AccountController::class, 'create']);
Route::post('account/view', [AccountController::class, 'view']);
Route::post('account/delete', [AccountController::class, 'delete']);
Route::post('account/edit', [AccountController::class, 'edit']);
Route::post('account/change-property', [AccountController::class, 'changeProperty']);

Route::post('leads', [LeadController::class, 'index']);
Route::post('lead/create', [LeadController::class, 'create']);
Route::post('lead/view', [LeadController::class, 'view']);
Route::post('lead/delete', [LeadController::class, 'delete']);
Route::post('lead/edit', [LeadController::class, 'edit']);
Route::post('lead/change-state', [LeadController::class, 'changeState']);

Route::post('templates', [TemplateController::class, 'index']);
Route::post('template/delete', [TemplateController::class, 'delete']);
Route::post('template/create', [TemplateController::class, 'create']);
Route::post('template/upload-file', [TemplateController::class, 'uploadFile']);

Route::post('proxies', [ProxyController::class, 'index']);
Route::post('proxy/create', [ProxyController::class, 'create']);
Route::post('proxy/view', [ProxyController::class, 'view']);
Route::post('proxy/delete', [ProxyController::class, 'delete']);
Route::post('proxy/edit', [ProxyController::class, 'edit']);

Route::post('threads', [ThreadController::class, 'index']);
Route::post('thread/view', [ThreadController::class, 'view']);

Route::post('messages', [MessageController::class, 'index']);
Route::post('command/create-custom-message', [CommandController::class, 'createCustomMessage']);
Route::post('command/create-custom-message-with-message_id', [CommandController::class, 'createCustomMessageWithMsgId']);
Route::post('command/create-get-directs', [CommandController::class, 'createGetDirects']);
Route::post('command/create-upload-loom', [CommandController::class, 'createUploadLoom']);

Route::post('looms', [LoomController::class, 'index']);
Route::post('loom/delete', [LoomController::class, 'delete']);
Route::post('loom/view', [LoomController::class, 'view']);

Route::post('dashboard/dm-statistics', [DashboardController::class, 'getDailyDmStatistics']);
Route::post('dashboard/running-accounts', [DashboardController::class, 'getRunningAccounts']);

Route::post('spintaxes', [SpintaxController::class, 'index']);
Route::post('spintaxe/view', [SpintaxController::class, 'view']);
Route::post('spintaxe/create', [SpintaxController::class, 'create']);



Route::post('clis', [CliController::class, 'index']);

