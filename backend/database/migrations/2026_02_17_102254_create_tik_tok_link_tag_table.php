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
        Schema::create('tik_tok_link_tag', function (Blueprint $table) {

            $table->foreignId('tik_tok_link_id')
                ->constrained()
                ->cascadeOnDelete();

            $table->foreignId('tik_tok_tag_id')
                ->constrained()
                ->cascadeOnDelete();

            $table->primary(['tik_tok_link_id','tik_tok_tag_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('tik_tok_link_tag');
    }
};
