<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Command;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('commands', function (Blueprint $table) {
            $table->id();

            $table->foreignId('account_id')
                ->nullable()
                ->constrained('accounts')
                ->cascadeOnDelete();

            $table->foreignId('lead_id')
                ->nullable()
                ->constrained('leads')
                ->nullOnDelete();

            $table->integer('commandable_id')->nullable();
            $table->string('commandable_type')->nullable();

            $table->integer('times')->default(0);

            $table->enum('type', Command::$types);
            $table->enum('state', Command::$states);

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('commands');
    }
};
