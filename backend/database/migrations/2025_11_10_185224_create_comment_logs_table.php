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
        Schema::create('comment_logs', function (Blueprint $table) {
            $table->id();

            $table->foreignId('order_id')
                ->nullable()
                ->constrained('orders')
                ->nullOnDelete();

            $table->foreignId('comment_id')
                ->nullable()
                ->constrained('order_comments')
                ->nullOnDelete();

            $table->foreignId('account_id')
                ->nullable()
                ->constrained('accounts')
                ->nullOnDelete();

            $table->enum('status', ['pending', 'sent', 'failed'])->default('pending');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('comment_logs');
    }
};
