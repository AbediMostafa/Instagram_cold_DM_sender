<?php

namespace App\Http\Controllers;

use App\Http\Resources\account\AccountCollection;
use App\Models\Account;
use App\Models\Message;
use App\Models\Notif;
use App\Models\Proxy;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AccountController extends Controller
{
    public function index()
    {
        return Account::query()
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
            ])
            ->select(
                'accounts.id', 'accounts.avatar_changed', 'accounts.username', 'accounts.instagram_state',
                'accounts.name', 'accounts.app_state', 'accounts.log', 'accounts.is_active', 'accounts.password',
                'accounts.email','accounts.secret_key',
                DB::raw('MIN(CASE WHEN messages.state = \'unseen\' THEN 0 ELSE 1 END) as priority'))
            ->leftJoin('threads', 'accounts.id', '=', 'threads.account_id')
            ->leftJoin('messages', 'threads.id', '=', 'messages.thread_id')
            ->groupBy('accounts.id')
            ->orderBy('priority', 'ASC')
            ->orderBy('accounts.created_at', 'DESC')
            ->paginate(
                config('data.pagination.each_page.accounts')
            );
    }

    public function view()
    {
        return Account::query()->select(
            'username', 'password', 'name', 'bio', 'id', 'avatar_changed',
            'instagram_state', 'app_state', 'is_active', 'created_at'
        )
            ->with(['templates' => function ($query) {
                $query->where('type', 'avatar')->first();
            }])
            ->withCount([
                'commands as following_count' => fn($_) => $_->where('type', 'follow')->where('state', 'success'),
                'commands as image_post_count' => fn($_) => $_->where('type', 'post image')->where('state', 'success'),
                'commands as dm_count' => fn($_) => $_->where('type', 'dm follow up')->where('state', 'success'),
                'commands as successful_commands' => fn($_) => $_->where('state', 'success'),
                'commands as total_commands',
            ])
            ->find(r('id'));
    }

    public function create()
    {
        if (request('bulk_insertion')) {
            r()->validate([
                'accounts' => 'required',
            ]);
        } else {
            r()->validate([
                'username' => 'required|unique:accounts',
                'password' => 'required'
            ]);
        }

        return tryCatch(
            fn() => r('bulk_insertion') ? Account::createBulk() : Account::createOne(),
            'Account created successfully',
        );
    }


    public function delete()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('ids'))
                ->delete(),
            'Account(s) deleted successfully',
        );
    }

    public function edit()
    {
        r()->validate([
            'username' => 'required|unique:accounts,username,' . r('id')
        ]);

        return tryCatch(
            fn() => Account::query()
                ->where('id', r('id'))
                ->update([
                    'username' => r('username'),
                    'password' => r('password'),
                    'instagram_state' => r('instagram_state'),
                ]),
            'Account updated successfully',
        );
    }

    public function changeProperty()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('ids'))
                ->update([
                    r('key') => r('value')
                ]),
            r('msg'),
        );
    }
}
