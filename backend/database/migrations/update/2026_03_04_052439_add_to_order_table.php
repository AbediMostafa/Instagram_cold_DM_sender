<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->json('action_data')->nullable()->after('description');

            $table->tinyInteger('is_prepared')->default(0)->after('action_data');

            $table->index(['service_type', 'is_prepared', 'status']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropIndex(['service_type', 'is_prepared', 'status']);
            $table->dropColumn(['action_data', 'is_prepared']);
        });
    }
};
