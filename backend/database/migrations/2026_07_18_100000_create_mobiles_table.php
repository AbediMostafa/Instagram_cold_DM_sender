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
        Schema::create('mobiles', function (Blueprint $table) {
            $table->id();

            // DuoPlus id; used as `phone_id` in every API call.
            $table->string('duo_id')->unique();

            // Display name for the panel, e.g. "Device_1".
            $table->string('name');

            // Last physical device status reported by DuoPlus cloudPhone/status:
            // 0=Not configured, 1=Powered on, 2=Powered off, 3=Expired,
            // 4=Renewal needed, 10=Powering on, 11=Configuring, 12=Config failed.
            // Only 1 is usable. Written by the central status sync + boot polling.
            $table->integer('status')->default(0)->index();

            // Logical worker state (mirror of the account app_state on web):
            // idle / processing / error. Independent from `status` above.
            $table->string('app_state')->default('idle')->index();

            $table->foreignId('proxy_id')
                ->nullable()
                ->constrained('proxies')
                ->nullOnDelete();

            $table->timestamp('created_at')->useCurrent();

            // Heartbeat: touched by the worker on every cycle so a stuck
            // app_state=processing can be reset based on staleness (phase 9).
            $table->dateTime('updated_at')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('mobiles');
    }
};
