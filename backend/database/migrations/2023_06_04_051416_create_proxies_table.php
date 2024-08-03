<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Proxy;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('proxies', function (Blueprint $table) {
            $table->id();
            $table->ipAddress('ip');
            $table->integer('port');
            $table->string('username');
            $table->string('password');
            $table->enum('state', Proxy::$states)->default('active');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('proxies');
    }
};
