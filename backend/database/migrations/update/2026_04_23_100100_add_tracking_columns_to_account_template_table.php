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
        Schema::table('account_template', function (Blueprint $table) {
            $table->enum('status', ['pending', 'processing', 'completed'])
                ->default('pending')
                ->after('template_id');

            $table->string('url')->nullable()->after('status');

            $table->unsignedBigInteger('like_count')->default(0)->after('url');
            $table->unsignedBigInteger('comment_count')->default(0)->after('like_count');
            $table->unsignedBigInteger('view_count')->default(0)->after('comment_count');
            $table->unsignedBigInteger('save_count')->default(0)->after('view_count');
            $table->unsignedBigInteger('repost_count')->default(0)->after('save_count');

            $table->jsonb('stats')->nullable()->after('repost_count');


            $table->timestamp('created_at')->nullable()->after('stats');
            $table->timestamp('updated_at')->nullable()->after('created_at');

            $table->index('status', 'idx_account_template_status');
        });

        DB::table('account_template')->update(['status' => 'completed']);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('account_template', function (Blueprint $table) {
            $table->dropIndex('idx_account_template_status');

            $table->dropColumn([
                'status',
                'url',
                'like_count',
                'comment_count',
                'view_count',
                'save_count',
                'repost_count',
                'stats',
                'created_at',
                'updated_at',
            ]);
        });
    }
};
