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
        Schema::create('tik_tok_links', function (Blueprint $table) {
            $table->id();
            $table->string('name')->nullable();
            $table->string('offer')->nullable();
            $table->string('spark_id')->nullable();
            $table->string('geo')->nullable();
            $table->text('post_link');
            $table->text('error')->nullable();
            $table->unsignedInteger('comments')->default(0);
            $table->unsignedInteger('likes')->default(0);
            $table->unsignedInteger('shares')->default(0);
            $table->unsignedInteger('saves')->default(0);
            $table->unsignedInteger('play_counts')->default(0);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('tik_tok_links');
    }
};
