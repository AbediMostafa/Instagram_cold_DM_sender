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
        Schema::create('enriched_leads', function (Blueprint $table) {
            $table->id();
            $table->string('company_name')->nullable();
            $table->string('website')->nullable();
            $table->string('linkedin_url')->nullable();
            $table->string('industry')->nullable();
            $table->string('company_size')->nullable();
            $table->string('headquarters')->nullable();
            $table->string('type')->nullable();
            $table->string('founded')->nullable();
            $table->string('instagram_username')->nullable();

            $table->text('specialties')->nullable();
            $table->text('about_us')->nullable();

            $table->unsignedTinyInteger('is_used')->default(0);

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('enriched_leads');
    }
};
