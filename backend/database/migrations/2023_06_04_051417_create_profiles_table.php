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
        Schema::create('profiles', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->string('folder')->nullable();
            $table->string('profile_id');
            $table->string('profile_number');
            $table->unsignedTinyInteger('is_used')->default(0);

            $table->foreignId('proxy_id')
                ->nullable()
                ->constrained('proxies')
                ->nullOnDelete();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('profiles');
    }
};
