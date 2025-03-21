<?php

namespace App\Http\Controllers;

use App\Classes\MultiloginService;
use App\Http\Resources\account\AccountCollection;
use App\Models\Account;
use App\Models\Message;
use App\Models\Notif;
use App\Models\Proxy;
use Carbon\Carbon;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

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
                'id', 'avatar_changed', 'username', 'instagram_state', 'email',
                'name', 'password', 'created_at','category_id',
                'secret_key', 'proxy_id', 'profile_id', 'has_enough_posts')
            ->withCount([
                'commands as total_cold_dms' => function ($query) use ($startDate, $endDate) {
                    $query->where('type', 'dm follow up')
                        ->where('times', 0)
                        ->where('state', 'success')
                        ->whereBetween('created_at', [$startDate, $endDate]);
                },

                'commands as total_follow_ups' => function ($query) use ($startDate, $endDate) {
                    $query->where('type', 'dm follow up')
                        ->where('times', '>', 0)
                        ->where('state', 'success')
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
                'profile:id,title',
                'category:id,title',
                'proxy:id,ip',
                'tags:id,title',
                'warnings' => function ($query) use ($startDate, $endDate) {
                    $query->select('created_at', 'account_id', 'cause')
                        ->orderByDesc('created_at');
                }
            ])
            ->when(
                r('filter'),
                fn($_) => $_->whereIn('instagram_state', r('filter'))
            )
            ->when(
                r('search'),
                function ($_) {
                    if (r('type') === 'proxy') {
                        $_->whereHas('proxy', fn($__) => $__->where('ip', likeOperator(), '%' . r('search') . '%'));
                    }

                    if (r('type') === 'account') {
                        $_->where('username', likeOperator(), '%' . r('search') . '%');
                    }

                    if (r('type') === 'profile') {
                        $_->whereHas('profile', fn($__) => $__->where('title', likeOperator(), '%' . r('search') . '%'));
                    }
                }
            )
            ->when(
                r('tags'),
                fn($_) => $_->whereHas('tags', fn($_) => $_->whereIn('id', r('tags')))
            )
            ->orderBy('id', 'DESC')
//            ->orderBy(r('sortBy'), r('sortDesc') ? 'DESC' : 'ASC')
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
            'instagram_state', 'app_state', 'is_active', 'created_at')
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
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
            'username', 'password',
            'instagram_state', 'app_state', 'color_id', 'is_used',
            'avatar_changed', 'username_changed', 'initial_posts_deleted',
            'has_enough_posts', 'next_login'
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
        return tryCatch(function () {

            Account::query()
                ->whereIn('id', r('ids'))
                ->get()
                ->each(function ($account) {
                    $account->delete();
                    $account->profile && $account->profile->deleteRecords();
                    sleep(3);
                });
        },
            'Account(s) deleted successfully'
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
                    'color_id' => r('color_id'),
                    'is_used' => r('is_used'),
                    'avatar_changed' => r('avatar_changed'),
                    'username_changed' => r('username_changed'),
                    'has_enough_posts' => r('has_enough_posts'),
                ]),
            'Account updated successfully',
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

    public function deleteWarning()
    {
        return tryCatch(
            function () {
                $accounts = Account::whereIn('id', r('ids'))->get();

                foreach ($accounts as $account) {
                    $account->warnings()->delete();
                }
            },
            'Warning(s) deleted successfully',
            'Problem updating account',
        );

    }

    public function makeActive()
    {
        return tryCatch(
            fn() => Account::whereIn('id', r('ids'))->get()
                ->each(fn($account) => $account->makeActive()),
            'Warning(s) deleted successfully',
            'Problem updating account',
        );
    }

    public function clearNextLogin()
    {
        return tryCatch(
            function () {
                Account::whereIn('id', r('ids'))
                    ->get()
                    ->each(function (Account $account) {
                        $account->next_login = null;
                        $account->save();
                    });
            },
            'Next login deleted successfully',
            'Problem updating account',
        );

    }

    public function fetchAccounts()
    {
        return Account::query()
            ->select('id', 'username')
            ->where('username', 'like', '%' . request('q') . '%')
            ->get();
    }

    public function clearProfile()
    {
        return tryCatch(
            function () {
                $accounts = Account::whereIn('id', r('ids'))->get();

                foreach ($accounts as $account) {
                    $account->profile_id = null;
                    $account->save();
                }
            },
            'Profile(s) deleted successfully',
            'Problem updating account',
        );
    }

    public function get2faCode()
    {
        try {
            $secretKey = r('secretKey');

            $resp = Http::withoutVerifying()->get("https://bulkacc.com/TwoFactorEnable/Get2FACode?secretKey=$secretKey");
            return $resp->json()['data']['otp'];

        } catch (\Exception $exception) {

            return "Error getting 2fa code : " . $exception->getMessage();
        }
    }

    public function getProxyApi()
    {
        return Account::query()->find(r('id'))->getProxy();
    }

    public function changeProfileProxyToResidentialApi()
    {
        try {
            Account::query()->whereIn('id', r('ids'))
                ->get()
                ->each(
                    fn(Account $account) => $account->updateProfileProxyToResidential()
                );
            return jsonSuccess('Account(s) Profile proxies updated successfully');

        } catch (\Exception $exception) {
            return jsonError($exception->getMessage() . $exception->getTraceAsString());
        }
    }

    public function changeProfileProxyToCustom()
    {
        try {
            Account::query()->whereIn('id', r('ids'))
                ->get()
                ->each(
                    fn(Account $account) => $account->updateProfileProxyToCustom()
                );
            return jsonSuccess('Account(s) Profile proxies updated successfully');

        } catch (\Exception $exception) {
            return jsonError($exception->getMessage() . $exception->getTraceAsString());
        }
    }

    public function startProfile()
    {

        try {
            $service = new MultiloginService();

            Account::query()
                ->whereIn('id', r('ids'))
                ->get()
                ->each(function (Account $account) use (&$service) {
                    runPythonProcess('new.py', $account->id);
//                    $account->profile ?
//                        $service->startProfile($account->profile->profile_id) :
//                        $service->addMessage("{$account->username} dont have profile");
                });

            return jsonSuccess('Profiles started ' . $service->getMessages());

        } catch (Exception $e) {

            return jsonError($e->getMessage());
        }
    }
}


