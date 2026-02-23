<?php

namespace App\Console\Commands;

use App\Models\OrderAction;
use Illuminate\Console\Command;
use Carbon\Carbon;

class ReleaseStuckActions extends Command
{
    protected $signature = 'orders:release-stuck {--minutes=6}';
    protected $description = 'Reset actions stuck in processing state';

    public function handle()
    {
        \Log::info("test",[]);
        $minutes = $this->option('minutes');
        $threshold = Carbon::now()->subMinutes($minutes);

        $count = OrderAction::query()
            ->where('status', 'processing')
            ->whereNotNull('updated_at')
            ->where('updated_at', '<', $threshold)
            ->update([
                'status' => 'free',
                'account_id' => null
            ]);

        if ($count > 0) {
            $this->info("Released {$count} stuck actions");
        }
    }
}
