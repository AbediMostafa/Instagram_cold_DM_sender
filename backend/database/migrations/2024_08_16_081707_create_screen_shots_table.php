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
        Schema::create('screen_shots', function (Blueprint $table) {
            $table->id();
            $table->string('cause');
            $table->string('path');

            $table->foreignId('account_id')
                ->constrained()
                ->cascadeOnDelete();

            $table->timestamp('created_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('screen_shots');
    }
};
