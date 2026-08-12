<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    /**
     * Mobile-side tunables, mirroring how the web side keeps timings and batch
     * sizes in the settings table. Timings are wall-clock budgets on purpose:
     * every DuoPlus call takes >1s, so these are read by the Python workers as
     * seconds of real time.
     */
    private array $settings = [
        // Stuck-reset: release app_state=processing older than this (15 min).
        // A worker touches updated_at between accounts, so this only fires when
        // the worker actually died.
        ['key' => 'mobile_stuck_timeout_seconds', 'value' => '900',
         'description' => 'Seconds before a stuck processing mobile is reset to idle'],

        // ExploreAndLike: open a random number of posts in [min,max] per run,
        // liking each with the given probability, then the module is done.
        ['key' => 'mobile_explore_min_posts', 'value' => '7',
         'description' => 'Minimum posts to view per ExploreAndLike run'],
        ['key' => 'mobile_explore_max_posts', 'value' => '12',
         'description' => 'Maximum posts to view per ExploreAndLike run'],
        ['key' => 'mobile_explore_like_chance', 'value' => '0.2',
         'description' => 'Probability of liking each opened post (0.2 = 20%)'],

        // How long to stay on each post before swiping on. Long dwells are
        // what make a session read as real viewing rather than a crawl.
        ['key' => 'mobile_explore_min_dwell', 'value' => '8',
         'description' => 'Minimum seconds to stay on a post before swiping'],
        ['key' => 'mobile_explore_max_dwell', 'value' => '20',
         'description' => 'Maximum seconds to stay on a post before swiping'],
    ];

    public function up(): void
    {
        foreach ($this->settings as $s) {
            // Idempotent: skip keys already present so re-running is safe and
            // an operator's tuned value is never clobbered.
            $exists = DB::table('settings')
                ->where('key', $s['key'])
                ->exists();

            if (!$exists) {
                DB::table('settings')->insert([
                    'type' => 'text',
                    'category' => null,
                    'key' => $s['key'],
                    'value' => $s['value'],
                    'description' => $s['description'],
                ]);
            }
        }
    }

    public function down(): void
    {
        $keys = array_column($this->settings, 'key');
        DB::table('settings')->whereIn('key', $keys)->delete();
    }
};
