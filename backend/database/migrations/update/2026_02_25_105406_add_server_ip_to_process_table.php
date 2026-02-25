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
        Schema::table('processes', function (Blueprint $table) {
            $table->dropUnique(['pid']);
        });

        Schema::table('processes', function (Blueprint $table) {
            $table->string('server_ip', 45)->after('pid')->default('0.0.0.0');
        });

        Schema::table('processes', function (Blueprint $table) {
            $table->unique(['pid', 'server_ip']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('processes', function (Blueprint $table) {
            $table->dropUnique(['pid', 'server_ip']);
            $table->dropColumn('server_ip');
            $table->unique(['pid']);
        });
    }
};
