<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Panel control for mobile workers, mirroring what the processes table
     * gives the web side.
     *
     * The mobiles table already carries two states, and these are a third and
     * fourth concern, kept separate on purpose:
     *   status    - physical device state from DuoPlus (sync-managed)
     *   app_state - logical worker state: idle/processing/error (worker-managed)
     *   is_active - operator's start/stop switch (panel-managed)
     *   pid/server_ip - which process on which machine currently owns the device
     */
    public function up(): void
    {
        Schema::table('mobiles', function (Blueprint $table) {
            // Operator switch. A worker whose device is inactive parks itself
            // and sleeps instead of running sessions, and the launcher skips
            // it entirely — the remote on/off the web side gets via
            // processes.status.
            $table->boolean('is_active')
                ->default(true)
                ->after('app_state')
                ->index();

            // Who is driving this device right now. Written by the worker on
            // every cycle so the panel can show where each device is running
            // and spot orphaned rows.
            $table->bigInteger('pid')->nullable()->after('is_active');
            $table->string('server_ip', 45)->nullable()->after('pid');
        });
    }

    public function down(): void
    {
        Schema::table('mobiles', function (Blueprint $table) {
            $table->dropColumn(['is_active', 'pid', 'server_ip']);
        });
    }
};
