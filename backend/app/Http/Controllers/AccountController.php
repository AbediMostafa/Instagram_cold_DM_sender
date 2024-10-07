<?php

namespace App\Http\Controllers;

use App\Http\Resources\account\AccountCollection;
use App\Models\Account;
use App\Models\Message;
use App\Models\Notif;
use App\Models\Proxy;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AccountController extends Controller
{
    public function index()
    {
        if (r('dateRange')) {
            $startDate = Carbon::parse(r('dateRange')[0])->startOfDay();
            $endDate = Carbon::parse(r('dateRange')[1])->endOfDay();
        } else {
            // Default to today
            $startDate = Carbon::today()->startOfDay();
            $endDate = Carbon::today()->endOfDay();
        }

        $accounts = Account::query()
            ->select(
                'id', 'avatar_changed', 'username', 'instagram_state',
                'name', 'app_state', 'log', 'is_active', 'password', 'created_at',
                'secret_key', 'category_id')
            ->withCount([
                'commands as total_cold_dms' => function ($query) use ($startDate, $endDate) {
                    $query->where('type', 'dm follow up')
                        ->where('times', 0)
                        ->whereBetween('created_at', [$startDate, $endDate]);
                },

                'commands as total_follow_ups' => function ($query) use ($startDate, $endDate) {
                    $query->where('type', 'dm follow up')
                        ->whereIn('times', [1, 2, 3])
                        ->whereBetween('created_at', [$startDate, $endDate]);
                },

                'threads as total_replies' => function ($query) use ($startDate, $endDate) {
                    $query->whereHas('messages', function ($subQuery) use ($startDate, $endDate) {
                        $subQuery->where('sender', 'lead')
                            ->where('type', 'text')
                            ->whereBetween('created_at', [$startDate, $endDate]);
                    });
                }
            ])
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
                'category:id,title',
                'warnings' => function ($query) use ($startDate, $endDate) {
                    $query->select('created_at', 'account_id')
                        ->orderByDesc('created_at');
                }
            ])
            ->when(
                r('filter'),
                fn($_) => $_->whereIn('instagram_state', r('filter'))
            )
            ->when(
                r('search'),
                fn($_) => $_->where('username', 'like', '%' . r('search') . '%')
            )
            ->orderBy(r('sortBy'), r('sortDesc') ? 'DESC' : 'ASC')
            ->paginate(
                config('data.pagination.each_page.accounts')
            );

        $accounts->getCollection()->transform(function ($account) {
            $account->created_at_ago = $account->created_at?->diffForHumans();

            $latestWarningCreatedAt = $account->warnings->first()->created_at ?? null;
            $account->latest_warning_created_at_ago = $latestWarningCreatedAt ? Carbon::parse($latestWarningCreatedAt)->diffForHumans() : 'No warnings';

            return $account;
        });

        return $accounts;
    }

    public function view()
    {
        return Account::query()->select(
            'username', 'password', 'name', 'bio', 'id', 'avatar_changed',
            'instagram_state', 'app_state', 'is_active', 'created_at', 'category_id'
        )
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
                'category:id,title',
            ])
            ->withCount([
                'commands as following_count' => fn($_) => $_->where('type', 'follow')->where('state', 'success'),
                'commands as image_post_count' => fn($_) => $_->where('type', 'post image')->where('state', 'success'),
                'commands as dm_count' => fn($_) => $_->where('type', 'dm follow up')->where('state', 'success'),
                'commands as successful_commands' => fn($_) => $_->where('state', 'success'),
                'commands as total_commands',
            ])
            ->find(r('id'));
    }

    public function getAccount()
    {
        return Account::query()->select(
            'username', 'password', 'category_id',
            'instagram_state', 'app_state',
        )
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
                    'category_id' => r('category_id'),
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

    public function setCategory()
    {
        return tryCatch(
            fn() => Account::query()
                ->whereIn('id', r('accountIds'))
                ->update([
                    'category_id' => r('categoryId'),
                ]),
            'Account updated successfully',
            'Problem updating account',
        );
    }
}


