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
        Schema::create('clis', function (Blueprint $table) {

            $table->id();

            $table->foreignId('account_id')
                ->nullable()
                ->constrained('accounts')
                ->cascadeOnDelete();

            $table->foreignId('process_id')
                ->nullable()
                ->constrained('processes')
                ->nullOnDelete();

            $table->string('log');

            $table->timestamp('created_at')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('clis');
    }
};
