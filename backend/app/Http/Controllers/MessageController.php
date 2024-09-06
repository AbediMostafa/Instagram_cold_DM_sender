<?php

namespace App\Http\Controllers;

use App\Models\Message;
use Illuminate\Http\Request;

class MessageController extends Controller
{
    public function index()
    {
        return Message::query()
            ->select('id', 'text', 'thread_id', 'sender', 'state', 'created_at')
            ->with(['thread.account', 'thread.lead'])
            ->when(
                r('filters'),
                fn($_) => $_->where('sender', 'lead')
                    ->whereHas(
                        'thread.lead',
                        fn($_) => $_->whereIn('last_state', r('filters'))
                    )
            )
            ->when(
                r('search.text'),
                function ($_) {
                    if (r('search.type') === 'lead') {
                        $_->whereHas('thread.lead', fn($__) => $__->where('username', 'like', '%' . r('search.text') . '%'));
                    }

                    if (r('search.type') === 'account') {
                        $_->whereHas('thread.account', fn($__) => $__->where('username', 'like', '%' . r('search.text') . '%'));
                    }

                    if (r('search.type') === 'message') {
                        $_->where('text', 'like', '%' . r('search.text') . '%');
                    }
                }
            )
            ->orderByRaw("
                CASE state
                WHEN 'unseen' THEN 1
                WHEN 'pending' THEN 2
                WHEN 'seen' THEN 3
                END ASC
            ")
            ->orderBy('sender', 'DESC')
            ->orderBy('created_at', 'DESC')
            ->paginate(
                config('data.pagination.each_page.messages')
            );
    }
}
