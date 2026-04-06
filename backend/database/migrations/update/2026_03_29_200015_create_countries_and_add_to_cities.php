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
        Schema::create('countries', function (Blueprint $table) {
            $table->id();
            $table->string('country_code')->unique();
            $table->string('name');
            $table->string('slug');

            $table->unsignedTinyInteger('is_used')->default(0);
            $table->timestamps();
        });

        Schema::table('cities', function (Blueprint $table) {
            $table->foreignId('country_id')
                ->nullable()
                ->after('slug')
                ->constrained('countries')
                ->nullOnDelete();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('cities', function (Blueprint $table) {
            $table->dropConstrainedForeignId('country_id');
        });

        Schema::dropIfExists('countries');
    }
};
