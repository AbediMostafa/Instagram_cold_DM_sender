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
        Schema::create('charity_leads', function (Blueprint $table) {
            $table->id();
            $table->string('lead_type');
            $table->unsignedTinyInteger('is_used')->default(0);
            $table->unsignedTinyInteger('duplicated_record')->default(0);

            $table->string('first_name')->nullable();
            $table->string('last_name')->nullable();
            $table->string('company_name')->nullable();
            $table->string('phone_number')->nullable();
            $table->string('website')->nullable();
            $table->string('email')->nullable();
            $table->string('linkedin')->nullable()->unique();

            $table->string('instagram')->nullable()->unique();

            $table->jsonb('data');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('charity_leads');
    }
};
