<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('locks', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique();
            $table->timestamp('locked_until')->nullable();
            $table->timestamps();
        });

        // Insert default locks
        DB::table('locks')->insert([
            [
                'name' => 'account_reset',
                'locked_until' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'name' => 'proxy_reset',
                'locked_until' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'name' => 'profile_reset',
                'locked_until' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('locks');
    }
};
