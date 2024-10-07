<?php

namespace App\Http\Controllers;

use App\Models\Lead;
use App\Models\Message;
use App\Models\Thread;
use \App\Casts\MessageDateCast;
use Illuminate\Support\Facades\DB;

class ThreadController extends Controller
{
    public function getThreads()
    {

        return Thread::select(
            'threads.*',
            DB::raw('MAX(CASE WHEN messages.state = "unseen" THEN messages.created_at ELSE NULL END) as latest_unseen_message_created_at')
        )
            ->leftJoin('messages', 'threads.id', '=', 'messages.thread_id')
            ->with([
                'account:id,username',
                'category:id,title',
                'lead:id,username,last_state',
                'messages' => function ($query) {
                    $query->orderBy('created_at', 'ASC'); // Load messages ordered by creation date
                }
            ])
            ->when(
                r('filters'),
                fn($_) => $_->whereHas(
                    'lead',
                    fn($_) => $_->whereIn('last_state', r('filters'))
                )
            )
            ->when(
                r('search.text'),
                function ($_) {
                    if (r('search.type') === 'lead') {
                        $_->whereHas('lead', fn($__) => $__->where('username', 'like', '%' . r('search.text') . '%'));
                    }

                    if (r('search.type') === 'account') {
                        $_->whereHas('account', fn($__) => $__->where('username', 'like', '%' . r('search.text') . '%'));
                    }

                    if (r('search.type') === 'message') {
                        $_->whereHas('messages', fn($_) => $_->where('text', 'like', '%' . r('search.text') . '%'));
                    }
                }
            )
            ->when(
                r('search.category_id'),
                fn($_) => $_->where('category_id', r('search.category_id'))
            )
            ->groupBy('threads.id')
            ->orderByRaw('latest_unseen_message_created_at DESC')
            ->paginate(10);


    }


    public function getLoomThreads()
    {
        return Thread::select(
            'threads.*',
            DB::raw('MAX(CASE WHEN messages.state = "unseen" THEN messages.created_at ELSE NULL END) as latest_unseen_message_created_at')
        )
            ->leftJoin('messages', 'threads.id', '=', 'messages.thread_id')
            ->with([
                'category:id,title',
                'account:id,username',
                'lead:id,username,last_state',
                'messages' => function ($query) {
                    $query->orderBy('created_at', 'ASC'); // Load messages ordered by creation date
                }
            ])
            ->whereHas(
                'lead',
                fn($_) => $_->whereIn('last_state', ['loom follow up', 'unseen loom reply', 'seen loom reply'])
            )
            ->when(
                r('filters'),
                fn($_) => $_->whereHas(
                    'lead',
                    fn($_) => $_->whereIn('last_state', r('filters'))
                )
            )
            ->when(
                r('search.text'),
                function ($_) {
                    if (r('search.type') === 'lead') {
                        $_->whereHas('lead', fn($__) => $__->where('username', 'like', '%' . r('search.text') . '%'));
                    }

                    if (r('search.type') === 'account') {
                        $_->whereHas('account', fn($__) => $__->where('username', 'like', '%' . r('search.text') . '%'));
                    }

                    if (r('search.type') === 'message') {
                        $_->whereHas('messages', fn($_) => $_->where('text', 'like', '%' . r('search.text') . '%'));
                    }
                }
            )
            ->when(
                r('search.category_id'),
                fn($_) => $_->where('category_id', r('search.category_id'))
            )
            ->groupBy('threads.id')
            ->orderByRaw('latest_unseen_message_created_at DESC')
            ->paginate(10);
    }

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

                $thread->makeSeenUnseenMessages();

                return $thread->messages;
            });

        } catch (\Exception $e) {
            return jsonError($e->getMessage());
        }
    }

    public function setCategory()
    {

        return tryCatch(
            fn() => Thread::query()
                ->whereIn('id', r('ThreadIds'))
                ->update([
                    'category_id' => r('categoryId'),
                ]),
            'Threads(s) updated successfully',
            'Problem updating Threads(s)',
        );

    }
}
