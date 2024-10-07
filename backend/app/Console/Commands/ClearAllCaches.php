<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class ClearAllCaches extends Command
{
    // Command name that can be called from terminal
    protected $signature = 'clear-caches';

    // Command description
    protected $description = 'Clear all caches including config, view, route, and compiled files';

    // Execute the console command
    public function handle()
    {
        $this->call('cache:clear');
        $this->call('view:clear');
        $this->call('route:clear');
        $this->call('clear-compiled');
        $this->call('config:cache');

        $this->info('All caches have been cleared!');
    }
}
