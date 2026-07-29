<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Mobile workers register in the processes table exactly like web workers,
     * so they inherit the whole control surface for free: the panel already
     * lists processes, assigns a workflow and flips status between
     * running/stopped/idle/terminated.
     *
     * The only thing a process row can't express yet is WHICH cloud phone it
     * drives — on the web side processes are interchangeable, on mobile each
     * one is pinned to a device. Hence this single column; nothing needs to be
     * added to the mobiles table, which stays pure device inventory.
     */
    public function up(): void
    {
        Schema::table('processes', function (Blueprint $table) {
            $table->foreignId('mobile_id')
                ->nullable()
                ->after('workflow_id')
                ->constrained('mobiles')
                ->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::table('processes', function (Blueprint $table) {
            $table->dropConstrainedForeignId('mobile_id');
        });
    }
};
