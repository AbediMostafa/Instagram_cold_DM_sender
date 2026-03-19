<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Add upload_post_status column to the accounts table.
     *
     * This field controls the connection lifecycle with the Upload-Post service:
     *   - none:          Default. No action has been taken.
     *   - pending:       Admin selected this account for connection.
     *   - connecting:    Worker claimed and is running the OAuth flow.
     *   - connected:     OAuth completed. Ready for video uploads.
     *   - failed:        Connection attempt failed (retryable).
     *   - disconnecting: Admin requested disconnection. Worker will call delete API.
     */
    public function up(): void
    {
        Schema::table('accounts', function (Blueprint $table) {
//            $table->string('upload_post_status')->default('none');
            $table->string('upload_post_username')->nullable();

//            $table->index('upload_post_status', 'idx_accounts_upload_post_status');
        });
    }

    /**
     * Reverse the migration.
     */
    public function down(): void
    {
        Schema::table('accounts', function (Blueprint $table) {
            $table->dropIndex('idx_accounts_upload_post_status');
            $table->dropColumn('upload_post_username');
            $table->dropColumn('upload_post_status');
        });
    }
};
