<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Order;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('sadeghi_telegram_orders', function (Blueprint $table) {
            $table->id();
            $table->enum('service_type', ['comment', 'like', 'like_and_comment', 'follow', 'view']);
            $table->text('target_link')->nullable();
            $table->integer('total_count')->default(0);
            $table->integer('completed_count')->default(0);
            $table->enum('status', Order::$statuses)->default('Pending');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('sadeghi_telegram_orders');
    }
};
