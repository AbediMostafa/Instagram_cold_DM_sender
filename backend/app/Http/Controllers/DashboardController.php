<?php

namespace App\Http\Controllers;

use App\Models\Account;
use Illuminate\Support\Facades\DB;
use \App\Models\Command;

class DashboardController extends Controller
{
    public function getDailyDmStatistics()
    {
        return Command::query()
            ->select(
                DB::raw('DATE(created_at) as date'),
                DB::raw("count(case when type = 'dm follow up' and times = 0 then 1 end) as total_cold_dms"),
                DB::raw("count(case when type = 'dm follow up' and times = 0 and state = 'success' then 1 end) as successful_cold_dms"),
                DB::raw("count(case when type = 'dm follow up' and times = 0 and state = 'fail' then 1 end) as failed_cold_dms"),
                DB::raw("count(case when type = 'dm follow up' and times = 1 and state = 'success' then 1 end) as first_follow_ups"),
                DB::raw("count(case when type = 'dm follow up' and times = 2 and state = 'success' then 1 end) as second_follow_ups"),
                DB::raw("count(case when type = 'dm follow up' and times = 3 and state = 'success' then 1 end) as third_follow_ups"),
                DB::raw("count(case when type = 'loom follow up' and times = 0 and state = 'success' then 1 end) as successful_loom_follow_ups")
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
}
