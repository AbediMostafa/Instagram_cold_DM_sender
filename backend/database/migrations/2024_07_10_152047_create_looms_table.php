<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Loom;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('looms', function (Blueprint $table) {
            $table->id();
            $table->string('hashed_name');
            $table->string('original_name');
            $table->string('path');
            $table->text('description')->nullable();
            $table->enum('state', Loom::$states)->default('pending');

            $table->foreignId('account_id')
                ->nullable()
                ->constrained()
                ->nullOnDelete();

            $table->foreignId('lead_id')
                ->nullable()
                ->constrained()
                ->nullOnDelete();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('looms');
    }
};
