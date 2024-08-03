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
                        fn($_)=>$_->whereIn('last_state', r('filters'))
                    )
            )
            ->orderByRaw("
                CASE state
                WHEN 'unseen' THEN 1
                WHEN 'pending' THEN 2
                WHEN 'seen' THEN 3
                END ASC
            ")
            ->orderBy('created_at', 'DESC')
            ->paginate(
                config('data.pagination.each_page.messages')
            );
    }
}
