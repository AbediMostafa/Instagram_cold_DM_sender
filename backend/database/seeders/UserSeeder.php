<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        User::query()->insert([
            [
                'name' => 'Bot',
                'email' => 'Bot',
                'password' => 'dm123!@#dm',
            ],

            [
                'name' => 'Admin',
                'email' => 'admin@admin.admin',
                'password' => 'dm123!@#dm',
            ],

        ]);
    }
}
