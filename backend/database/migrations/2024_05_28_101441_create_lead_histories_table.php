<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Lead;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('lead_histories', function (Blueprint $table) {
            $table->id();

            $table->enum('state', Lead::$states)->default('free');
            $table->integer('times')->nullable()->default(0);

            $table->foreignId('lead_id')
                ->constrained()
                ->cascadeOnDelete();

            $table->foreignId('account_id')
                ->nullable()
                ->constrained()
                ->cascadeOnDelete();

            $table->foreignId('user_id')
                ->nullable()
                ->constrained()
                ->cascadeOnDelete();

            $table->timestamp('created_at')->useCurrent();

        });
    }
    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('lead_histories');
    }
};
