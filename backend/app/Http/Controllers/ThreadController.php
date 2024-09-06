<?php

namespace App\Http\Controllers;

use App\Models\Message;
use App\Models\Thread;
use \App\Casts\MessageDateCast;
use Illuminate\Support\Facades\DB;

class ThreadController extends Controller
{
    public function index()
    {
        return Thread::query()
            ->where('account_id', r('account_id'))
            ->with(['lead:id,username,last_state'])
            ->joinSub(
                'select thread_id, max(created_at) as latest_message_time from messages group by thread_id',
                'latest_messages',
                'threads.id',
                '=',
                'latest_messages.thread_id',
            )
            ->withCount([
                'messages',
                'messages as unread_messages_count' => fn($_) => $_->where('sender', 'lead')->where('state', 'unseen')
            ])
            ->when(r('search'),
                fn($_) => $_->whereHas('lead',
                    fn($_) => $_->where('username', 'like', '%' . r('search') . '%')
                )
            )
            ->orderBy('unread_messages_count', 'DESC')
            ->orderBy('latest_message_time', 'DESC')
            ->paginate(10);
    }

    public function view()
    {
        try {
            return DB::transaction(function () {
                Message::query()
                    ->where('thread_id', r('thread_id'))
                    ->where('state', 'unseen')
                    ->update(['state' => 'seen']);

                $thread = Thread::query()
                    ->whereId(r('thread_id'))
                    ->with([
                        'messages' => fn($_) => $_->select(
                            'id', 'thread_id', 'text', 'type',
                            'sender', 'state', 'created_at',
                            'messageable_type', 'messageable_id',
                        )
                            ->with(['messageable:id,description,original_name,path,state'])
                    ])
                    ->first();

                $thread->lead->makeSeen();

                return $thread->messages;
            });

        } catch (\Exception $e) {
            return jsonError($e->getMessage());
        }
    }
}
