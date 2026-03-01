<?php

namespace App\Console\Commands;

use App\Models\Order;
use App\Models\OrderAction;
use Illuminate\Console\Command;
use Carbon\Carbon;
use Illuminate\Support\Facades\Log;

class ReleaseStuckActions extends Command
{
    protected $signature = 'orders:release-stuck {--minutes=6}';
    protected $description = 'Reset actions stuck in processing state';

    public function handle()
    {
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

        Order::query()
            ->withCount([
                'actions as sent_actions_count' => function ($q) {
                    $q->where('status', 'sent');
                }
            ])
            ->where('status', 'In progress')
            ->orderByDesc('id')
            ->limit(200)
            ->get()
            ->each(function (Order $order) {
                if ($order->total_count == $order->sent_actions_count && $order->is('In progress')) {
                    $order->setStatusTo('Completed');
                    Log::channel("incoming_requests")->info("Completed order : {$order->id}");
                }
            });

        Log::channel("incoming_requests")->info("Updated Counts : $count");

    }
}
