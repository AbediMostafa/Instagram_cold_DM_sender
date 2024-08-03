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
        Schema::create('dms', function (Blueprint $table) {
            $table->id();

            $table->foreignId('account_id')->constrained();
            $table->foreignId('lead_id')->constrained();
            $table->text('text');
            $table->integer('times')->default(0);

            $table->timestamp('created_at')->useCurrent();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('dms');
    }
};
