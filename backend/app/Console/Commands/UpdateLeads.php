<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class UpdateLeads extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'leads:update';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Update leads that are older than 90 days';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        DB::statement("
            UPDATE public.leads
            SET
                times = 0,
                last_state = 'free',
                account_id = NULL,
                category_id = NULL,
                user_id = NULL,
                export_date = NULL,
                last_command_send_date = NULL
            WHERE export_date < NOW() - INTERVAL '90 days'
        ");

        $this->info('Leads older than 90 days have been updated.');
    }
}
