<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Cli extends Model
{
    use HasFactory;

    // Optional: Protecting 'updated_at' from being mass-assigned
    protected $guarded = [];
    const UPDATED_AT = null;

    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s', // Change the format as needed
    ];

    public function account()
    {
        return $this->belongsTo(Account::class);
    }

    public function toArray()
    {
        $array = parent::toArray();

        // Ensure created_at is in Tehran timezone
        $array['created_at'] = $this->created_at->timezone('Asia/Tehran')->toDateTimeString();

        return $array;
    }
}
