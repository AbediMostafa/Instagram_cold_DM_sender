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
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->string('customer')->nullable();
            $table->enum('service_type', ['comment', 'like', 'like_and_comment', 'follow', 'view']);
            $table->text('target_link');
            $table->integer('start_count');
            $table->integer('total_count');
            $table->integer('completed_count')->default(0);
            $table->text('description')->nullable();
            $table->enum('status', ['Pending', 'In progress', 'Completed', 'Canceled'])->default('Pending');
            $table->timestamps();

        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
