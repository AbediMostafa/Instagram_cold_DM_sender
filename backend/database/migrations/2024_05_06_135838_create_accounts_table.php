<?php

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
        Schema::create('accounts', function (Blueprint $table) {
            $table->id();
            $table->string('secret_key')->nullable();
            $table->string('username')->unique();
            $table->string('email')->nullable();
            $table->string('password');
            $table->string('name')->nullable();
            $table->string('category')->nullable();
            $table->text('bio')->nullable();
            $table->text('profile_pic_url')->nullable();
            $table->enum('instagram_state', Account::$instagramStates)->default('active');
            $table->enum('app_state', Account::$appStates)->default('idle');

            $table->foreignId('proxy_id')
                ->nullable()
                ->constrained()
                ->nullOnDelete();

            $table->unsignedTinyInteger('is_used')->default(0);
            $table->unsignedTinyInteger('avatar_changed')->default(0);
            $table->unsignedTinyInteger('username_changed')->default(0);
            $table->unsignedTinyInteger('initial_posts_deleted')->default(0);
            $table->unsignedTinyInteger('is_active')->default(1);
            $table->text('web_session')->nullable();
            $table->text('mobile_session')->nullable();
            $table->text('log')->nullable();
            $table->timestamps();
            $table->timestamp('last_login')->nullable();
            $table->timestamp('next_login')->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('accounts');
    }
};
