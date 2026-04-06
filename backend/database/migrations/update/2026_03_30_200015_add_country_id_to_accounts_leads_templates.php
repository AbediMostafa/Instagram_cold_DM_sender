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
        Schema::table('accounts', function (Blueprint $table) {
            $table->foreignId('country_id')
                ->nullable()
                ->after('service_id')
                ->constrained('countries')
                ->nullOnDelete();
        });

        Schema::table('leads', function (Blueprint $table) {
            $table->foreignId('country_id')
                ->nullable()
                ->after('category_id')
                ->constrained('countries')
                ->nullOnDelete();
        });

        Schema::table('templates', function (Blueprint $table) {
            $table->foreignId('country_id')
                ->nullable()
                ->after('category_id')
                ->constrained('countries')
                ->nullOnDelete();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('accounts', function (Blueprint $table) {
            $table->dropConstrainedForeignId('country_id');
        });

        Schema::table('leads', function (Blueprint $table) {
            $table->dropConstrainedForeignId('country_id');
        });

        Schema::table('templates', function (Blueprint $table) {
            $table->dropConstrainedForeignId('country_id');
        });
    }
};
