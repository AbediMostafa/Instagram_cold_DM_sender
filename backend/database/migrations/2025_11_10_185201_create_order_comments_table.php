<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('order_comments', function (Blueprint $table) {
            $table->id();

            $table->foreignId('order_id')
                ->nullable()
                ->constrained('orders')
                ->nullOnDelete();

            $table->text('content');

            $table->foreignId('account_id')
                ->nullable()
                ->constrained('accounts')
                ->nullOnDelete();

            $table->enum('status', ['free','pending', 'sent', 'failed'])->default('free');

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('order_comments');
    }
};
