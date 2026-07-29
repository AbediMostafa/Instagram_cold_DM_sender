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
        Schema::table('accounts', function (Blueprint $table) {
            // Fixed assignment: each account belongs to exactly one mobile
            // (max 10 active accounts per device — Instagram's per-device cap).
            // Web accounts keep mobile_id = null, so no atomic claim is needed
            // on the mobile side for accounts.
            $table->foreignId('mobile_id')
                ->nullable()
                ->after('service_id')
                ->constrained('mobiles')
                ->nullOnDelete();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('accounts', function (Blueprint $table) {
            $table->dropConstrainedForeignId('mobile_id');
        });
    }
};
