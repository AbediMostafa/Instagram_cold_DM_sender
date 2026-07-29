<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    /**
     * The orders.service_type column is a MySQL ENUM (see the original
     * create_orders_table migration). Laravel's Blueprint can't modify an enum
     * without doctrine/dbal, so we alter it with raw SQL. On PostgreSQL the
     * same column is a varchar with a CHECK constraint, so we rebuild that
     * constraint instead.
     */
    private array $types = [
        'comment', 'like', 'like_and_comment', 'follow', 'view',
        'view_story', 'save_post', 'comment_and_reply', 'share',
    ];

    public function up(): void
    {
        $this->setEnum($this->types);
    }

    public function down(): void
    {
        // Dropping 'share' will fail if any share orders exist — that's
        // intentional; delete them first if you really need to roll back.
        $this->setEnum(array_diff($this->types, ['share']));
    }

    private function setEnum(array $types): void
    {
        $quoted = "'" . implode("','", $types) . "'";

        if (DB::getDriverName() === 'pgsql') {
            DB::statement('ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_service_type_check');
            DB::statement("ALTER TABLE orders ADD CONSTRAINT orders_service_type_check CHECK (service_type::text = ANY (ARRAY[{$quoted}]::text[]))");
            return;
        }

        DB::statement("ALTER TABLE orders MODIFY service_type ENUM({$quoted}) NOT NULL");
    }
};
