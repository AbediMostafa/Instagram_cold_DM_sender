<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {

    public function up(): void
    {
        Schema::table('order_actions', function (Blueprint $table) {
            $table->index(['account_id', 'order_id'], 'idx_order_actions_account_order');
            $table->index(['type', 'status', 'order_id'], 'idx_order_actions_type_status_order');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('order_actions', function (Blueprint $table) {
            $table->dropIndex('idx_order_actions_account_order');
            $table->dropIndex('idx_order_actions_type_status_order');
        });
    }
};
