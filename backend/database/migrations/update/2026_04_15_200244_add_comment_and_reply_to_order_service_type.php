<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    /**
     * Add 'comment_and_reply' to the service_type column on orders table
     */
    public function up(): void
    {
        DB::statement("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_service_type_check");

        DB::statement("ALTER TABLE orders ADD CONSTRAINT orders_service_type_check CHECK (service_type::text = ANY (ARRAY[
            'comment'::text, 'like'::text, 'like_and_comment'::text, 'follow'::text,
            'view'::text, 'view_story'::text, 'save_post'::text, 'comment_and_reply'::text
        ]))");
    }

    /**
     * Remove 'comment_and_reply' from the service_type constraint.
     */
    public function down(): void
    {
        DB::statement("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_service_type_check");

        DB::statement("ALTER TABLE orders ADD CONSTRAINT orders_service_type_check CHECK (service_type::text = ANY (ARRAY[
            'comment'::text, 'like'::text, 'like_and_comment'::text, 'follow'::text,
            'view'::text, 'view_story'::text, 'save_post'::text
        ]))");
    }
};
