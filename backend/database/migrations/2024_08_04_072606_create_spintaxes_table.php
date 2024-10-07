<?php

use App\Models\Spintax;
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
        Schema::create('spintaxes', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique();
            $table->enum('type', Spintax::$types)->default('cold dm');
            $table->text('text');

            $table->foreignId('category_id')
                ->nullable()
                ->constrained()
                ->nullOnDelete();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('spintaxes');
    }
};
