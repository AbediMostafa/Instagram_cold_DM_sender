<?php

namespace App\Http\Controllers;

use App\Classes\LoomUploader;
use App\Models\Command;
use App\Models\Lead;
use App\Models\Loom;
use App\Models\Message;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use Symfony\Component\Process\Exception\ProcessFailedException;
use \Symfony\Component\Process\Process;

class CommandController extends Controller
{

    public function createCustomMessageWithMsgId()
    {
        try {
            return DB::transaction(function () {
                $message = Message::with('thread')
                    ->find(r('messageId'));

                $message = Message::query()->create([
                    'thread_id' => $message->thread_id,
                    'text' => r('text'),
                    'state' => 'pending',
                    'created_at' => Carbon::now()
                ]);

                $command = $message->command()
                    ->create([
                        'account_id' => $message->thread->account_id,
                        'lead_id' => $message->thread->lead_id,
                        'type' => 'custom message',
                        'state' => 'pending',
                    ]);

                DB::afterCommit(fn() => runPythonProcess('send_custom_message.py', $command->id));

            });
        } catch (\Exception $e) {

            return jsonError($e->getMessage());
        }

    }

    public function createCustomMessage()
    {
        try {
            return DB::transaction(function () {

                $message = Message::query()->create([
                    'thread_id' => r('thread_id'),
                    'text' => r('text'),
                    'state' => 'pending',
                    'created_at' => Carbon::now()
                ]);

                $command = $message->command()
                    ->create([
                        'account_id' => r('account_id'),
                        'lead_id' => r('lead_id'),
                        'type' => r('sendLoom') ? 'send loom' : 'custom message',
                        'state' => 'pending',
                    ]);

                if(r('sendLoom')){
                    $lead = Lead::query()
                        ->whereId(r('lead_id'))
                        ->update([
//                            'last_state'=>
                        ]);
                }


                DB::afterCommit(fn() => runPythonProcess('send_custom_message.py', $command->id));
            });
        } catch (\Exception $e) {

            return jsonError($e->getMessage());
        }
    }

    public function createGetDirects()
    {
        try {

//            $anotherPendingCommandExists = Command::query()
//                ->where('account_id', r('account_id'))
//                ->where('type', 'get threads')
//                ->where('state', 'pending')
//                ->exists();
//
//            abort_if($anotherPendingCommandExists, 422, 'Another pending refresh on this account exists');

            return DB::transaction(function () {

                $command = Command::query()
                    ->create([
                        'account_id' => r('account_id'),
                        'type' => 'get threads',
                        'state' => 'pending',
                        'created_at' => Carbon::now()
                    ]);

                DB::afterCommit(fn() => runPythonProcess('get_directs.py', $command->id));
            });

        } catch (\Exception $e) {
            return jsonError($e->getMessage());
        }
    }

    public function createUploadLoom()
    {
        $uploader = new LoomUploader();

        abort_if(
            $uploader->fileWithTheSameNameExists(),
            422,
            LoomUploader::$messages['file_exists']
        );

        try {

            return DB::transaction(function () use ($uploader) {
                $uploader->storeFileOnServer();

                if ($uploader->fileNotExists()) {
                    throw new \Exception(LoomUploader::$messages['storage_failed']);
                }

                $loomRecord = Loom::query()->create([
                    'hashed_name' => $uploader->file->hashName(),
                    'original_name' => $uploader->file->getClientOriginalName(),
                    'path' => $uploader->filePath,
                    'description' => r('description'),
                    'account_id' => r('account_id'),
                    'lead_id' => r('lead_id'),
                ]);

                $messageRecord = $loomRecord->message()->create([
                    'thread_id' => r('thread_id'),
                    'type' => 'loom',
                    'state' => 'pending',
                    'created_at' => Carbon::now(),
                ]);

                $command = $messageRecord->command()
                    ->create([
                        'account_id' => r('account_id'),
                        'lead_id' => r('lead_id'),
                        'type' => 'send loom',
                        'state' => 'pending',
                    ]);

                DB::afterCommit(fn() => runPythonProcess('send_loom.py', $command->id));
            });

        } catch (\Exception $e) {

            DB::rollback();
            $uploader->fileExists() && $uploader->deleteFile();
            abort(422, $e->getMessage());
        }
    }

}


