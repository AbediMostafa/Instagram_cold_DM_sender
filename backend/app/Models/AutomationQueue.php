<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class AutomationQueue extends Model
{
    use HasFactory;

    protected $guarded = [];
    protected $casts = [
        'payload' => 'array',
    ];

    public function account()
    {
        return $this->belongsTo(Account::class);
    }
}
