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
        Schema::create('account_specs', function (Blueprint $table) {
            $table->id();

            $table->foreignId('account_id')
                ->constrained('accounts')
                ->cascadeOnDelete();

            $table->unsignedInteger('reels_count')->default(0);
            $table->unsignedInteger('avg_reel_views')->default(0);
            $table->unsignedInteger('min_reel_views')->default(0);
            $table->unsignedInteger('max_reel_views')->default(0);
            $table->unsignedInteger('total_reel_views')->default(0);

            $table->timestamp('last_reels_scan_at')->nullable();

            $table->unique('account_id');;
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('account_specs');
    }
};
