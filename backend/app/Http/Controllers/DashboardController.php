<?php

namespace App\Http\Controllers;

use App\Models\Account;
use Illuminate\Support\Facades\DB;
use \App\Models\Command;

class DashboardController extends Controller
{
    public function getDailyDmStatistics()
    {
        // Get today's date
        $today = now()->format('Y-m-d');

        // Get the count of active accounts for today (you should replace this with the actual logic to count active accounts)
        $numberOfActiveAccounts = Account::whereInstagramState('active')->count(); // This should be your method to get the active accounts count

        // Use updateOrCreate to insert or update the 'active accounts' command for today
        Command::query()->updateOrCreate(
            [
                'type' => 'number of active accounts',
                'created_at' => now()->format('Y-m-d'),
            ],
            [
                'times' => $numberOfActiveAccounts,
                'state' => 'success',
                'updated_at' => now(),
            ]
        );

        return Command::query()
            ->select(
                DB::raw('DATE(created_at) as date'),
                DB::raw("count(case when type = 'dm follow up' and times = 0 then 1 end) as total_cold_dms"),
                DB::raw("count(case when type = 'dm follow up' and times = 0 and state = 'success' then 1 end) as successful_cold_dms"),
                DB::raw("count(case when type = 'dm follow up' and times = 0 and state = 'fail' then 1 end) as failed_cold_dms"),
                DB::raw("count(case when type = 'dm follow up' and times = 1 then 1 end) as total_first_follow_ups"),
                DB::raw("count(case when type = 'dm follow up' and times = 1 and state = 'success' then 1 end) as successful_first_follow_ups"),
                DB::raw("count(case when type = 'dm follow up' and times = 1 and state = 'fail' then 1 end) as failed_first_follow_ups"),
                DB::raw("count(case when type = 'dm follow up' and times = 2 and state = 'success' then 1 end) as second_follow_ups"),
                DB::raw("count(case when type = 'dm follow up' and times = 3 and state = 'success' then 1 end) as third_follow_ups"),
                DB::raw("count(case when type = 'loom follow up' and times = 0 and state = 'success' then 1 end) as looms_sent_out"),
                DB::raw("count(case when type = 'call booked' then 1 end) as call_booked"),
                DB::raw("MAX(case when type = 'number of active accounts' then times end) as active_accounts")

            )
            ->groupBy('date')
            ->orderBy('date', 'DESC')
            ->paginate(
                config('data.pagination.each_page.daily_dm_statistics')
            );
    }

    public function getRunningAccounts()
    {
        return Account::query()
            ->with([
                'templates' => fn($query) => $query->where('type', 'avatar')->first(),
            ])
            ->select(
                'accounts.id', 'accounts.avatar_changed', 'accounts.username', 'accounts.instagram_state',
                'accounts.name', 'accounts.app_state', 'accounts.log', 'accounts.is_active'
            )->where('app_state', '!=', 'idle')
            ->get();
    }

    public function addAccount()
    {

        return tryCatch(
            function () {

                $decodedAccounts = json_decode(request('account'), true);

                foreach ($decodedAccounts as $data) {
                    unset($data['id']);
                    $account = new Account();

                    $account->fill($data);

                    $account->save();
                }
            },
            'addedd successfully'
        );


    }
}
