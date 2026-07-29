<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * ALTER-only variant for databases that already ran the original
 * create_order_actions_table migration. New deployments get the column from
 * the updated create migration instead; do not run both blindly (the guard
 * below makes running both safe anyway).
 */
return new class extends Migration {
    public function up(): void
    {
        if (Schema::hasColumn('order_actions', 'count')) {
            return;
        }

        Schema::table('order_actions', function (Blueprint $table) {
            // Web actions are 1 unit each (default keeps them untouched);
            // mobile share actions carry a variable count per send.
            $table->unsignedInteger('count')->default(1)->after('type');
        });
    }

    public function down(): void
    {
        if (!Schema::hasColumn('order_actions', 'count')) {
            return;
        }

        Schema::table('order_actions', function (Blueprint $table) {
            $table->dropColumn('count');
        });
    }
};
