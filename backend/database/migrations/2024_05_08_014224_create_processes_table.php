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
        Schema::create('processes', function (Blueprint $table) {
            $table->id();
            $table->bigInteger('pid')->unsigned();
            $table->string('server_ip', 45);
            $table->enum('status', ['running', 'stopped', 'terminated', 'idle'])->default('idle');
            $table->string('proxy_type')->nullable();

            $table->foreignId('workflow_id')
                ->nullable()
                ->constrained('workflows')
                ->nullOnDelete();

            $table->timestamp('last_checked_at')->nullable()->useCurrent();
            $table->timestamp('created_at')->useCurrent();

            $table->unique(['pid', 'server_ip']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('processes');
    }
};
