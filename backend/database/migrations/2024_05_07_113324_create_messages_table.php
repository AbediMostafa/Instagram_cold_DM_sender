<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use \App\Models\Message;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('messages', function (Blueprint $table) {
            $table->id();
            $table->string('message_id')->nullable();

            $table->foreignId('thread_id')
                ->nullable()
                ->constrained('threads')
                ->cascadeOnDelete();

            $table->unsignedBigInteger('messageable_id')->nullable();
            $table->string('messageable_type')->nullable();

            $table->text('text')->nullable();
            $table->enum('sender', Message::$senders)->default('account');
            $table->enum('type', Message::$types)->default('text');
            $table->enum('state', Message::$states)->default('seen');
            $table->timestamp('created_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('messages');
    }
};
