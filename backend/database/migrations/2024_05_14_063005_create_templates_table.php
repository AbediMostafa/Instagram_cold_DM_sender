<?php

use \App\Models\Template;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Account;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('templates', function (Blueprint $table) {
            $table->id();
            $table->text('text');
            $table->text('caption')->nullable();
            $table->string('carousel_id')->nullable();
            $table->string('uid')->nullable();

            $table->foreignId('color_id')
                ->nullable()
                ->constrained('colors')
                ->nullOnDelete();

            $table->foreignId('category_id')
                ->nullable()
                ->constrained('categories')
                ->nullOnDelete();
            $table->unsignedTinyInteger('is_used')->default(0);
            $table->enum('type', Template::$types);
            $table->enum('sub_type', Template::$subTypes)->nullable();
            $table->timestamp('created_at')->nullable();
            $table->unique(['text', 'caption']);

        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('profile_information_templates');
    }
};
